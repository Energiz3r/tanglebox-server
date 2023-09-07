from settings import loadWebSettings
from endpoints import loadEndpoints
from eventStreamEndpoint import eventStreamRouteHandler
import logging
from flask import Flask, render_template, Response
import json
from utils import remove_keys_from_dict

app = None


def initWebServer(app):
    @app.route("/", methods=["GET"])
    def index():
        return render_template("index.html")

    @app.route("/available-endpoints", methods=["POST"])
    def fetchAvailableEndpoints():
        endpoints = loadEndpoints()
        endpointList = []
        for endpoint in endpoints:
            # don't expose this to clients!
            endpointList.append(
                remove_keys_from_dict(endpoint, ["serverAddress", "port"])
            )
        return Response(json.dumps(endpointList), content_type="application/json")

    for endpoint in loadEndpoints(True):
        if endpoint["isEnabled"]:
            eventStreamRouteHandler(
                app,
                f"{endpoint['type']}",
                f"{endpoint['urlSuffix']}",
                f"{endpoint['serverAddress']}",
                f"{endpoint['port']}",
                f"{endpoint['requiresAccessToken']}",
            )


log = None
if __name__ == "__main__":
    settings = loadWebSettings(True)
    app = Flask(__name__)
    initWebServer(app)

    # get rid of the API output
    if not settings["webDebugOutput"]:
        log = logging.getLogger("werkzeug")
        log.setLevel(logging.ERROR)
        app.logger.disabled = True
        log.disabled = True

    if settings["useSsl"]:
        app.run(host="0.0.0.0", port=settings["port"], ssl_context="adhoc")
    else:
        app.run(host="0.0.0.0", port=settings["port"])
