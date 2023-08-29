from settings import loadWebSettings
from endpoints import loadEndpoints
from eventStreamEndpoint import eventStreamRouteHandler
import logging
from flask import Flask, render_template, Response
import json
from utils import remove_keys_from_dict

app = None


def initWebServer(app, endpoints):
    @app.route("/", methods=["GET"])
    def index():
        return render_template("index.html")

    for endpoint in endpoints:
        eventStreamRouteHandler(
            app,
            f"{endpoint['type']}",
            f"{endpoint['name']}",
            f"{endpoint['serverAddress']}",
            f"{endpoint['port']}",
            f"{endpoint['requiresAccessToken']}",
        )

    @app.route("/available-endpoints", methods=["POST"])
    def fetchAvailableEndpoints():
        endpointList = []
        for endpoint in endpoints:
            # don't expose this to clients!
            endpointList.append(
                remove_keys_from_dict(endpoint, ["serverAddress", "port"])
            )
        return Response(json.dumps(endpointList), content_type="application/json")


log = None
if __name__ == "__main__":
    settings = loadWebSettings(True)
    endpoints = loadEndpoints(True)
    app = Flask(__name__)
    initWebServer(app, endpoints)

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
