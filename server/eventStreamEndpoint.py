from flask import request, Response, stream_with_context, abort
import requests
from settings import loadWebSettings
from utils import createChunk, checkApiToken
import uuid


def eventStreamRouteHandler(app, type, name, serverAddress, port, tokenRuleApplies):
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
        if data["prompt"]:
            ip = request.remote_addr
            print(f"({url}) From ({ip}):", data["prompt"])

        def generate():
            try:
                req = requests.post(url, json=data, stream=True)
                for chunk in req.iter_content(chunk_size=1024):
                    if chunk:
                        yield chunk
            except request.exceptions.RequestException as e:
                app.logger.error("Error reading from {0}: {1}".format(url, e))
                yield str(e)

        if data["stream"]:
            return Response(
                stream_with_context(generate()), content_type="text/event-stream"
            )
        else:
            return Response(generate(), content_type="application/json")

    eventStreamRoute.__name__ = str(uuid.uuid4())
    app.route(f"/{name}", methods=["POST"])(eventStreamRoute)
