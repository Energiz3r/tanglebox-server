import argparse
from languageModel import LanguageModel

from flask import Flask, render_template
from flask_sock import Sock

app = Flask(__name__)
socket = Sock(app)

languageModel = None
modelSettings = None


@socket.route("/echo")
def echo(ws):
    global languageModel
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
        elif "#-get-config-#" in data:
            print("Sent config to front end")
            ws.send("#-model-name-#" + modelSettings.modelName)
            ws.send("#-device-name-#" + modelSettings.device)
            ws.send("#-max-new-tokens-#" + str(modelSettings.max_new_tokens))
            ws.send("#-temperature-#" + str(modelSettings.temperature))
        else:
            ws.send("#a-c-k#")
            try:
                languageModel.runInference(data, ws)
            finally:
                ws.send("#f-i-n#")


@app.route("/")
def index():
    return render_template("index.html")


class ModelSettings:
    def __init__(self, temperature, max_new_tokens, modelName, device):
        self.temperature = temperature
        self.max_new_tokens = max_new_tokens
        self.modelName = modelName
        self.device = device

    def setTemp(self, temperature):
        self.temperature = temperature

    def setMaxTokens(self, max_new_tokens):
        self.max_new_tokens = max_new_tokens


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-name", type=str, default="facebook/opt-350m")
    parser.add_argument("--num-gpus", type=str, default="1")
    parser.add_argument(
        "--device", type=str, choices=["cuda", "cpu", "cpu-gptq", "mps"], default="cuda"
    )
    parser.add_argument("--conv-template", type=str, default="v1")
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--max-new-tokens", type=int, default=512)
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--llama", action="store_true")
    parser.add_argument(
        "--load-8bit", action="store_true", help="Use 8-bit quantization."
    )
    args = parser.parse_args()
    modelSettings = ModelSettings(
        args.temperature, args.max_new_tokens, args.model_name, args.device
    )
    languageModel = LanguageModel(
        args.model_name,
        args.num_gpus,
        args.device,
        args.debug,
        modelSettings,
        args.load_8bit,
        args.llama,
    )

    print(f"Starting flask + websockets ({args.port + 1})...")
    app.run(host="0.0.0.0", port=args.port)  # Start the server
