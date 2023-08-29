from settings import loadWebSettings
from eventStreamEndpoint import eventStreamRouteHandler
import logging
from flask import Flask, render_template

app = None


def initWebServer(app):
    @app.route("/", methods=["GET"])
    def index():
        return render_template("index.html")

    eventStreamRouteHandler(
        app, "/vicky65", "192.168.1.10", "64222", "/completion", False
    )
    eventStreamRouteHandler(app, "/vicky7", "127.0.0.1", "64223", None, False)


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
