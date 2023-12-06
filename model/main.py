from languageModel import LanguageModel
from settings import loadSettings
from transformersEndpoint import transformersRouteHandler
import logging
from flask import (
    Flask,
    render_template,
    Response,
)
import os


def initWebServer(app):
    global languageModel

    @app.route("/", methods=["GET"])
    def index():
        return render_template("index.html")

    @app.route("/reset", methods=["GET"])
    def resetModel():
        response = Response("Model reset initiated")

        @response.call_on_close
        def on_close():
            print("Killing process")
            os._exit(
                1
            )  # kill the whole process because torch and cuda won't free up VRAM otherwise

        return response

    transformersRouteHandler(app, "/", lambda: languageModel)


log = None
if __name__ == "__main__":
    app = Flask(__name__)

    initWebServer(app)

    settings = loadSettings(True)

    # get rid of the API output
    if not settings["enableModelDebugOutput"]:
        log = logging.getLogger("werkzeug")
        log.setLevel(logging.ERROR)
        app.logger.disabled = True
        log.disabled = True

    if not settings["maintenanceMode"]:
        languageModel = LanguageModel(
            settings["modelName"],
            settings["numberOfGpus"],
            settings["device"],
            settings["enableModelDebugOutput"],
            settings["use8BitCompression"],
            settings["vRamGb"],
        )

    app.run(host="0.0.0.0", port=settings["port"])
