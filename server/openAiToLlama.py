from flask import request, Response, stream_with_context, abort
import requests
from settings import loadWebSettings
from utils import createChunk
from endpoints import loadEndpoints
import uuid
import time
import json
import time
import pprint
from functions import getFunctionPrompt, getOutputObj, formatOpenAiRequest
import re

import os
from dotenv import load_dotenv
load_dotenv()

OPEN_AI_API_KEY = os.getenv('OPEN_AI_API_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

def openAiToLlama(app, queue):
    def eventStreamRoute():
        settings = loadWebSettings()
        if settings["maintenanceMode"]:
            return Response(
                createChunk(settings["maintenanceModeMessage"]),
                content_type="application/json",
            )
        
        endpoints = loadEndpoints()        
        data = request.get_json()

        if not "model" in data:
            abort(400, "Missing value 'model'")
        if not "messages" in data:
            abort(400, "'messages' missing from request")

        endpoint = None
        for endpointNow in endpoints:
            if endpointNow["urlSuffix"] == data["model"]:
                endpoint = endpointNow

        if endpoint == None:
            abort(400, "Endpoint error - endpoint not found")

        serverAddress = f"{endpoint['protocol']}://{endpoint['serverAddress']}:{endpoint['port']}"
        serverAddress = f"{serverAddress}/completion"

        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        if not ip:
            ip = request.remote_addr

        promptForDisplay = ""
        if "messages" in data:
            if "content" in data["messages"][-1]:
                promptForDisplay = data["messages"][-1]["content"]

        print(f"oai2l: ({endpoint['urlSuffix']}) From ({ip}):", promptForDisplay) 

        queue_id = uuid.uuid4()
        queue.add(queue_id)

        requestData, wasFunction = formatOpenAiRequest(data, abort)
        headers = {"Content-Type": "application/json", "Accept": "*/*"}

        def generateProxyStreamingResponse():

            for i in range(300):
                if not queue.check_ready(queue_id):
                    if (i%5 == 0):
                        print(f"oai2l: Task for {ip} waiting for slot", i, 'secs elapsed')
                    time.sleep(1)
                else:
                    break
        
            print(f"oai2l: Task for {ip} is starting")

            entireResponse = ""
            try:
                req = requests.post(serverAddress, json=requestData, headers=headers, stream=False, timeout=500)
                for chunk in req.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        responseObj = json.loads(chunk)
                        entireResponse = re.sub('\\\\_', '_', responseObj["content"].strip())
                        timings = responseObj["timings"]
                        usage = {
                            "prompt_tokens": timings["prompt_n"],
                            "prompt_time": timings["prompt_ms"] / 1000,
                            "completion_token": timings["predicted_n"],
                            "completion_time": timings["predicted_ms"] / 1000,
                            "total_tokens": timings["prompt_n"] + timings["predicted_n"],
                            "total_time": (timings["prompt_ms"] + timings["predicted_ms"]) / 1000
                        }
                        replyObj = getOutputObj(endpoint["urlSuffix"], usage, wasFunction, entireResponse)
                        yield json.dumps(replyObj)
            except Exception as e:
                app.logger.error("oai2l: Error reading from {0}: {1}".format(serverAddress, e))
                yield createChunk(str(e))
            finally:
                queue.complete(queue_id)
                print(f"oai2l: Task for {ip} finished!")
                print(f"oai2l: ({endpoint['urlSuffix']}) To ({ip}):", entireResponse)

        return Response(
            generateProxyStreamingResponse(), content_type="application/json"
        )

    eventStreamRoute.__name__ = str(uuid.uuid4())
    print("registering endpoint", f"/api/openai-to-llama")
    app.route(f"/api/openai-to-llama", methods=["POST"])(eventStreamRoute)
    app.route(f"/api/openai-to-llama/chat/completions", methods=["POST"])(eventStreamRoute)
