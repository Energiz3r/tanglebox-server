import argparse
from languageModel import LanguageModel
from runInference import websocketInference, inference
from checkApiToken import checkApiToken
from conversationTemplates import conversationTemplates
from settings import loadSettings
from conversationClass import Conversation

import logging
import json
import time

from flask import Flask, render_template, request, Response, stream_with_context, abort
from flask_sock import Sock

app = None
socket = None
log = None
languageModel = None
settings = None


def generate_response():
    start_time = time.time()
    while time.time() - start_time < 10:  # generate data for 10 seconds
        my_dict = {"message": "Hello, World!"}
        yield json.dumps(my_dict) + '\n'
        time.sleep(2)  # generate new data every 5 seconds

def initWebServer(app):
    @socket.route("/")
    def websocketHandler(ws):
        global languageModel
        modelName = settings['modelName']
        debug = settings['enableModelDebugOutput']
        template = settings['conversationTemplate']
        device = settings['device']
        newMaxTokens = settings['maxNewTokens']
        temperature = settings['temperature']
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
                ws.send("#-max-new-tokens-#" + str(modelSettings.maxNewTokens))
                ws.send("#-temperature-#" + str(modelSettings.temperature))
            elif settings['maintenanceMode']:
                ws.send("#a-c-k#")
                ws.send("Sorry, I am offline for maintenance. Please try again later.")
                ws.send("#f-i-n#")
            else:
                ws.send("#a-c-k#")
                #ws.send("Sorry, I am offline for maintenance. Please try again later.")
                try:
                    websocketInference(
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

    def generate_response():
        start_time = time.time()
        while time.time() - start_time < 10:  # generate data for 10 seconds
            my_dict = {"message": "Hello, World!"}
            yield json.dumps(my_dict) + '\n'
            time.sleep(2)  # generate new data every 5 seconds


    @app.route("/conversation", methods=['POST', "GET"])
    def conversationRoute():
        # params:
        # "token"
        # "systemPrompt"
        # "userPrompt"
        # "conversationHistory"
        # "conversationTemplate"
        # "temperature"
        # "maxNewTokens"
        # "shouldStreamResponse"
        # "messageSeparator"
        # "outputSeparator"
        global languageModel
        if request.method == 'POST':
            data = request.get_json()
        elif request.method == 'GET':
            data = request.args.to_dict()
        else:
            abort(405, "Method not allowed")
        print(data)
        if settings['isApiTokensRequired']:
            if not 'token' in data:
                abort(401, "Missing token")
            else:
                if not checkApiToken(data['token']):
                    abort(401, "Unaccepted token")
        if not "userPrompt" in data:
            abort(400, "Missing user prompt")
        if 'conversationTemplate' in data:
            if not data['conversationTemplate'] in conversationTemplates:
                abort(400, "Invalid conversation template. Must be one of: " + ", ".join(conversationTemplates.keys()))
            conversation = conversationTemplates[data['conversationTemplate']].copy()
        else:
            conversation = conversationTemplates[settings['conversationTemplate']].copy()
        if "conversationHistory" in data:
            try:
                conversation.messages.append([(item[0], item[1]) for item in data["conversationHistory"]])
            except:
                abort(400, "Bad conversation history JSON format. Should be: {['Role', 'Message'], ...}")
        if "messageSeparator" in data:
            conversation.sep = data["messageSeparator"]
        if "systemPrompt" in data:
            conversation.system = data["systemPrompt"]
        if "outputSeparator" in data:
            conversation.modelOutputSeparator = data["outputSeparator"]        
        
        conversation.append_message(conversation.roles[0], data["userPrompt"])
        conversation.append_message(conversation.roles[1], None)
        inputPrompt = conversation.getPromptForModel()
        outputPrompt = conversation.getPromptForOutput()
        separator = conversation.sep

        temperature = settings['temperature'] if not 'temperature' in data else data['temperature']
        maxNewTokens = settings['maxNewTokens'] if not 'maxNewTokens' in data else data['maxNewTokens']
        device = settings['device']
        debug = settings['enableModelDebugOutput']
        shouldStream = False if not 'shouldStream' in data else data['shouldStream']
        
        if not settings["maintenanceMode"]:
            result = inference(
                languageModel.model,
                languageModel.tokenizer,
                inputPrompt,
                outputPrompt,
                temperature,
                maxNewTokens,
                separator,
                device,
                debug,
                shouldStream,
            )
        else:
            result = "Maintenance mode"        

        if shouldStream:
            return Response(stream_with_context(result))
        else:
            return result


    @app.route("/")
    def index():
        return render_template("index.html")


class ModelSettings:
    def __init__(self, temperature, maxNewTokens, modelName, device, shouldStream):
        self.temperature = temperature
        self.maxNewTokens = maxNewTokens
        self.modelName = modelName
        self.device = device
        self.shouldStream = shouldStream

    def setTemp(self, temperature):
        self.temperature = temperature

    def setMaxTokens(self, maxNewTokens):
        self.maxNewTokens = maxNewTokens

    def setShouldStream(self, shouldStream):
        self.shouldStream = shouldStream


if __name__ == "__main__":
    settings = loadSettings()   

    app = Flask(__name__)
    socket = Sock(app)

    initWebServer(app)

    # get rid of the API output
    if not settings['enableWebLogOutput']:
        log = logging.getLogger("werkzeug")
        log.setLevel(logging.ERROR)
        app.logger.disabled = True
        log.disabled = True

    if not settings['maintenanceMode']:
        languageModel = LanguageModel(
            settings['modelName'],
            settings["numberOfGpus"],
            settings["device"],
            settings["enableModelDebugOutput"],
            settings["use8BitCompression"],
            settings["vRamGb"]
        )

    if settings['useSsl']:
        app.run(host="0.0.0.0", port=settings['port'], ssl_context="adhoc")
    else:
        app.run(host="0.0.0.0", port=settings['port'])
