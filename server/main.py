import argparse
from languageModel import LanguageModel
from runInference import runInference
from conversationTemplates import conversationTemplates
import logging

from flask import Flask, render_template
from flask_sock import Sock

app = Flask(__name__)
socket = Sock(app)

log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)
app.logger.disabled = True
log.disabled = True

languageModel = None


@socket.route("/")
def websocketHandler(ws):
    global languageModel
    args = parser.parse_args()
    debug = args.debug
    template = args.conv_template
    device = args.device
    modelName = args.model_name
    newMaxTokens = args.max_new_tokens
    temperature = args.temperature
    user = "[unknown]"
    try:
        user = (
            ws.environ["HTTP_X_REAL_IP"]
            + " "
            + ws.environ["HTTP_USER_AGENT"].split(" ")[0]
        )
        if debug:
            print("Connection from:", user)
    except:
        pass
    
    modelSettings = ModelSettings(
        temperature, newMaxTokens, modelName, device, True
    )
    if not conversationTemplates[template]:
        template = "vicuna1.1"
    if debug:
        print("Using conversation template:",template)
    conversation = conversationTemplates[template].copy()
    if debug:
        print("Ready for processing data")

    while True:
        data = ws.receive()
        if "#-ping-#" in data:
            ws.send("#-pong-#")
        elif "#-set-temp-#" in data:
            newTemp = data.replace("#-set-temp-#", "")
            if debug:
                print("Set temp", newTemp)
            modelSettings.setTemp(float(newTemp))
            ws.send("#-set-#")
        elif "#-set-max-tokens-#" in data:
            newMaxTokens = data.replace("#-set-max-tokens-#", "")
            if debug:
                print("Set max tokens", newMaxTokens)
            modelSettings.setMaxTokens(int(newMaxTokens))
            ws.send("#-set-#")
        elif "#-set-streaming-#" in data:
            shouldStream = data.replace("#-set-streaming-#", "")
            if debug:
                print("Set streaming: ", shouldStream)
            modelSettings.setShouldStream(True if shouldStream == "true" else False)
            ws.send("#-set-#")
        elif "#-delete-#" in data:
            conversation = conversationTemplates[template].copy()
            ws.send("#-delete-#")
            if debug:
                print("Deleted user's conversation.")
        elif "#-get-config-#" in data:
            # print("Sent config to front end")
            ws.send("#-model-name-#" + modelSettings.modelName)
            ws.send("#-device-name-#" + modelSettings.device)
            ws.send("#-max-new-tokens-#" + str(modelSettings.max_new_tokens))
            ws.send("#-temperature-#" + str(modelSettings.temperature))
        elif args.maintenance:
            ws.send("#a-c-k#")
            ws.send("Sorry, I am offline for maintenance. Please try again later.")
            ws.send("#f-i-n#")
        else:
            ws.send("#a-c-k#")
            #ws.send("Sorry, I am offline for maintenance. Please try again later.")
            try:
                runInference(
                    data,
                    ws,
                    modelSettings,
                    conversation,
                    languageModel.tokenizer,
                    languageModel.model,
                    device,
                    debug,
                    user
                )
            except:
                try:
                    conv = conversation.getPromptForModel()
                    lengthOfPrompt = len(conv)
                    print("Error fetching response. Conversation:", lengthOfPrompt)
                    approxNumOfTokens = len(conv.split(" "))
                    print("Approx number of tokens:", approxNumOfTokens)
                    ws.send(f"There was an error fetching a response. Length of prompt (chars): {lengthOfPrompt}, approx # of tokens: {approxNumOfTokens}")
                except:
                    ws.send("There was an error fetching a response.")
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
    parser.add_argument("--conv-template", type=str, default="vicuna1.1")
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--max-new-tokens", type=int, default=512)
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--maintenance", action="store_true")
    parser.add_argument("--ssl", action="store_true")
    parser.add_argument(
        "--load-8bit", action="store_true", help="Use 8-bit quantization."
    )
    parser.add_argument("--vram-gb", type=int, default=13)
    args = parser.parse_args()

    if not args.maintenance:
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
