from flask import request, Response, stream_with_context, abort
import requests
from settings import loadWebSettings
from utils import createChunk, parseChunkContent, checkApiToken
from endpoints import loadEndpoints
import uuid
import time

import os
from dotenv import load_dotenv
load_dotenv()

OPEN_AI_API_KEY = os.getenv('OPEN_AI_API_KEY')

def eventStreamRouteHandler(app, endpoint, urlPrefix, queue):
    def eventStreamRoute():
        settings = loadWebSettings()
        if settings["maintenanceMode"]:
            return Response(
                createChunk(settings["maintenanceModeMessage"]),
                content_type="application/json",
            )
        
        type = endpoint['type']
        isOpenAi = type == "openai"
        serverAddress = f"{endpoint['protocol']}://{endpoint['serverAddress']}:{endpoint['port']}"
        if type == "openai":
            serverAddress = f"{endpoint['protocol']}://{endpoint['serverAddress']}"
        if type == "llamacpp":
            serverAddress = f"{serverAddress}/completion"

        endpoints = loadEndpoints()
        tokenRuleApplies = False
        for endpointNow in endpoints:
            if endpointNow["urlSuffix"] == endpoint["urlSuffix"]:
                tokenRuleApplies = endpointNow["requiresAccessToken"]
                if not endpointNow["isEnabled"]:
                    return Response(
                        createChunk(endpoint["motd"]),
                        content_type="application/json",
                    )

        data = request.get_json()

        if tokenRuleApplies and settings["enableTokenRules"]:
            if not "token" in data:
                abort(400, "Missing value 'token'")
            if not checkApiToken(data["token"]):
                abort(400, "Invalid token supplied")

        if isOpenAi:
            if not "messages" in data:
                abort(400, "Messages array missing from request")
            if not "content" in data["messages"][-1]:
                print(data)
                abort(400, "Messages array empty")
        else:
            if not "prompt" in data:
                abort(400, "Prompt missing from request")
        
        shouldStream = "stream" in data and data["stream"]

        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        if not ip:
            ip = request.remote_addr
        if type == "openai":
            shouldStream = False
            promptForDisplay = ""
            if "messages" in data:
                if "content" in data["messages"][-1]:
                    promptForDisplay = data["messages"][-1]["content"]
        else:
            promptForDisplay = (
                data["prompt"] if not "promptInputOnly" in data else data["promptInputOnly"]
            )

        print(f"({endpoint['urlSuffix']}) From ({ip}):", promptForDisplay)

        if isOpenAi:
            data["model"] = endpoint["label"]

        if type == "llamacpp":
            queue_id = uuid.uuid4()
            queue.add(queue_id)

        def generateProxyStreamingResponse():

            if type == "llamacpp":
                for i in range(300):
                    if not queue.check_ready(queue_id):
                        if (i%5 == 0):
                            print(f"Task for {ip} waiting for slot", i, 'secs elapsed')
                        time.sleep(1)
                        if shouldStream:
                            yield createChunk("waiting in queue")
                    else:
                        break
            
                print(f"Task for {ip} is starting")

            entireResponse = ""
            try:
                if isOpenAi:
                    headers = {'Authorization': f'Bearer {OPEN_AI_API_KEY}'}
                else:
                    headers = {}
                req = requests.post(serverAddress, json=data, stream=True, headers=headers, timeout=500)
                for chunk in req.iter_content(chunk_size=1024 * 1024):
                    if shouldStream:
                        shutdown_callback = request.environ.get(
                            "werkzeug.server.shutdown"
                        )
                        if shutdown_callback and not chunk:
                            print("Connection terminated by client")
                            req.close()
                    if chunk:
                        entireResponse += parseChunkContent(chunk, isOpenAi)
                        yield chunk
            except Exception as e: # request.exceptions.RequestException as e:
                app.logger.error("Error reading from {0}: {1}".format(serverAddress, e))
                yield createChunk(str(e))
            finally:
                if type == "llamacpp":
                    queue.complete(queue_id)
                    print(f"Task for {ip} finished!")
                print(f"({endpoint['urlSuffix']}) To ({ip}):", entireResponse)

        if shouldStream:
            return Response(
                stream_with_context(generateProxyStreamingResponse()),
                content_type="text/event-stream",
            )
        else:
            return Response(
                generateProxyStreamingResponse(), content_type="application/json"
            )

    eventStreamRoute.__name__ = str(uuid.uuid4())
    print("registering endpoint", f"/{urlPrefix}{endpoint['urlSuffix']}")
    app.route(f"/{urlPrefix}{endpoint['urlSuffix']}", methods=["POST"])(eventStreamRoute)
