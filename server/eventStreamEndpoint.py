from flask import request, Response, stream_with_context, abort
import requests
from settings import loadWebSettings
from utils import createChunk, parseChunkContent, checkApiToken
from endpoints import loadEndpoints
import uuid

bearerToken = "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"

def eventStreamRouteHandler(app, endpoint, urlPrefix):
    def eventStreamRoute():
        settings = loadWebSettings()
        if settings["maintenanceMode"]:
            return Response(
                createChunk(settings["maintenanceModeMessage"]),
                content_type="application/json",
            )

        type = endpoint['type']
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

        if type == "openai":
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
                if "message" in data["messages"][-1]:
                    promptForDisplay = data["messages"][-1]["content"]
        else:
            promptForDisplay = (
                data["prompt"] if not "promptInputOnly" in data else data["promptInputOnly"]
            )

        print(f"({endpoint['urlSuffix']}) From ({ip}):", promptForDisplay)

        if type == "openai":
            data["model"] = endpoint["label"]

        def generateProxyStreamingResponse():
            entireResponse = ""
            try:
                if type == "openai":
                    headers = {'Authorization': f'Bearer {bearerToken}'}
                else:
                    headers = {}
                req = requests.post(serverAddress, json=data, stream=True, headers=headers)
                for chunk in req.iter_content(chunk_size=1024):
                    if shouldStream:
                        shutdown_callback = request.environ.get(
                            "werkzeug.server.shutdown"
                        )
                        if shutdown_callback and not chunk:
                            print("Connection terminated by client")
                            req.close()
                    if chunk:
                        entireResponse += parseChunkContent(chunk)
                        yield chunk
            except request.exceptions.RequestException as e:
                app.logger.error("Error reading from {0}: {1}".format(serverAddress, e))
                yield str(e)
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
