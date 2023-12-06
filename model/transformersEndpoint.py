from flask import request, Response, stream_with_context, abort, current_app
from runInference import inference
from settings import loadSettings


def transformersRouteHandler(app, url, getLanguageModel):
    @app.route(url, methods=["POST"])
    def transformersRoute():
        settings = loadSettings()
        languageModel = getLanguageModel()
        data = request.get_json()
        if not "prompt" in data:
            abort(400, "Missing prompt")
        ip = request.remote_addr if not "id" in data else data["id"]
        print(f"From ({ip}): '{data['prompt']}'")

        if "stop" not in data:
            stopTokens = ["</s>", "ASSISTANT:", "USER:"]
        else:
            stopArray = data.get("stop", [])
            if len(stopArray) == 3:
                stopTokens = stopArray
            else:
                abort(400, "Stop tokens invalid")
        if settings["enableModelDebugOutput"]:
            print("stops are:", stopTokens)
        temperature = 0.7 if not "temperature" in data else data["temperature"]
        maxNewTokens = 512 if not "n_predict" in data else data["n_predict"]
        device = settings["device"]
        debug = settings["enableModelDebugOutput"]
        shouldStream = False if not "stream" in data else data["stream"]

        if not settings["maintenanceMode"]:
            generator = inference(
                languageModel.model,
                languageModel.tokenizer,
                data["prompt"],
                stopTokens,
                temperature,
                maxNewTokens,
                device,
                debug,
                shouldStream,
                ip,
            )
        else:
            abort(503, settings["maintenanceModeMessage"])

        if shouldStream:
            return Response(
                stream_with_context(generator), content_type="text/event-stream"
            )
        else:
            result = ""
            for value in generator:
                result = value
            return result
