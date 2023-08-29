from languageModel import LanguageModel
from settings import loadSettings
from transformersEndpoint import transformersRouteHandler
import logging
from flask import Flask, render_template

app = None
languageModel = None
settings = None


def initWebServer(app):
    global settings, languageModel

    @app.route("/", methods=["GET"])
    def index():
        return render_template("index.html")

    transformersRouteHandler(app, "/", settings, lambda: languageModel)


log = None
if __name__ == "__main__":
    settings = loadSettings()
    app = Flask(__name__)
    initWebServer(app)

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
