from flask import request, Response, stream_with_context, abort
import requests
from settings import loadWebSettings
from utils import createChunk, parseChunkContent, checkApiToken
import uuid


def eventStreamRouteHandler(
    app, type, urlSuffix, serverAddress, port, tokenRuleApplies
):
    def eventStreamRoute():
        settings = loadWebSettings()
        if settings["maintenanceMode"]:
            return Response(
                createChunk(settings["maintenanceModeMessage"]),
                content_type="application/json",
            )
        data = request.get_json()
        if tokenRuleApplies and settings["shouldRequireToken"]:
            if not "token" in data:
                abort(400, "Missing value 'token'")
            if not checkApiToken(data["token"]):
                abort(400, "Invalid token supplied")
        if not "prompt" in data:
            abort(400, "Prompt missing from request")
        if type == "llamacpp":
            url = f"http://{serverAddress}:{port}/completion"
        else:
            url = f"http://{serverAddress}:{port}"
        shouldStream = "stream" in data and data["stream"]

        ip = request.remote_addr
        promptForDisplay = (
            data["prompt"] if not "promptInputOnly" in data else data["promptInputOnly"]
        )
        print(f"({urlSuffix}) From ({ip}):", promptForDisplay)

        def generateProxyStreamingResponse():
            entireResponse = ""
            try:
                req = requests.post(url, json=data, stream=True)
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
                app.logger.error("Error reading from {0}: {1}".format(url, e))
                yield str(e)
            print(f"({urlSuffix}) To ({ip}):", entireResponse)

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
    app.route(f"/{urlSuffix}", methods=["POST"])(eventStreamRoute)
