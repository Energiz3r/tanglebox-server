import argparse
from languageModel import LanguageModel
from runInference import runInference
import uuid
from convos import convoTemplates

from flask import Flask, render_template
from flask_sock import Sock

app = Flask(__name__)
socket = Sock(app)

languageModel = None


@socket.route("/")
def websocketHandler(ws):
    global languageModel
    id = uuid.uuid4()
    args = parser.parse_args()
    modelSettings = ModelSettings(
        args.temperature, args.max_new_tokens, args.model_name, args.device, True
    )

    if args.eos:
        print("Using alternate conversation template")
        conversation = convoTemplates["v11"].copy()
    else:
        conversation = convoTemplates["v1"].copy()
    while True:
        data = ws.receive()
        if "#-set-temp-#" in data:
            newTemp = data.replace("#-set-temp-#", "")
            print("Set temp", newTemp)
            modelSettings.setTemp(float(newTemp))
            ws.send("#-set-#")
        elif "#-set-max-tokens-#" in data:
            newMaxTokens = data.replace("#-set-max-tokens-#", "")
            print("Set max tokens", newMaxTokens)
            modelSettings.setMaxTokens(int(newMaxTokens))
            ws.send("#-set-#")
        elif "#-set-streaming-#" in data:
            shouldStream = data.replace("#-set-streaming-#", "")
            print("Set streaming: ", shouldStream)
            modelSettings.setShouldStream(True if shouldStream == "true" else False)
            ws.send("#-set-#")
        elif "#-delete-#" in data:
            conversation = convoTemplates["v1"].copy()
            ws.send("#-delete-#")
            print("Deleted user's conversation.")
        elif "#-get-config-#" in data:
            print("Sent config to front end")
            ws.send("#-model-name-#" + modelSettings.modelName)
            ws.send("#-device-name-#" + modelSettings.device)
            ws.send("#-max-new-tokens-#" + str(modelSettings.max_new_tokens))
            ws.send("#-temperature-#" + str(modelSettings.temperature))
        else:
            ws.send("#a-c-k#")
            try:
                runInference(
                    data,
                    ws,
                    modelSettings,
                    conversation,
                    languageModel.tokenizer,
                    languageModel.model,
                    args.device,
                    args.debug,
                )
            finally:
                ws.send("#f-i-n#")


@app.route("/")
def index():
    return render_template("index.html")


class ModelSettings:
    def __init__(self, temperature, max_new_tokens, modelName, device, shouldStream):
        self.temperature = temperature
        self.max_new_tokens = max_new_tokens
        self.modelName = modelName
        self.device = device
        self.shouldStream = shouldStream

    def setTemp(self, temperature):
        self.temperature = temperature

    def setMaxTokens(self, max_new_tokens):
        self.max_new_tokens = max_new_tokens

    def setShouldStream(self, shouldStream):
        self.shouldStream = shouldStream


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-name", type=str, default="facebook/opt-350m")
    parser.add_argument("--num-gpus", type=str, default="1")
    parser.add_argument(
        "--device",
        type=str,
        choices=["cuda", "cpu", "cpu-gptq", "mps", "cpu-ggml"],
        default="cuda",
    )
    parser.add_argument("--conv-template", type=str, default="v1")
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--max-new-tokens", type=int, default=512)
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--ssl", action="store_true")
    parser.add_argument("--eos", action="store_true")
    parser.add_argument(
        "--load-8bit", action="store_true", help="Use 8-bit quantization."
    )
    parser.add_argument("--vram-gb", type=int, default=13)
    args = parser.parse_args()

    languageModel = LanguageModel(
        args.model_name,
        args.num_gpus,
        args.device,
        args.debug,
        args.load_8bit,
        args.vram_gb,
    )

    if args.ssl:
        app.run(host="0.0.0.0", port=args.port, ssl_context="adhoc")
    else:
        app.run(host="0.0.0.0", port=args.port)
