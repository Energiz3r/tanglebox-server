from utils import printDictAsTable, remove_keys_from_dict
import json
import os


def loadEndpoints(shouldOutputSettings=False):
    json_filepath = "endpoints.json"
    default_data = [
        {
            "type": "transformers",
            "urlSuffix": "vicky7",
            "label": "vicky-7b",
            "isEnabled": True,
            "deviceName": "cuda",
            "protocol": "http",
            "serverAddress": "127.0.0.1",
            "port": "64223",
            "requiresAccessToken": False,
            "maxTokens": 2060,
            "userRole": "USER",
            "assistantRole": "ASSISTANT",
            "stopToken": "</s>",
            "separator": " ",
            "systemPrompt": "A chat between a curious user and an artificial intelligence assistant. The assistant gives helpful, detailed, and polite answers to the user's questions. ",
            "motd": "this is the 7B Vicky model running in fast mode",
            "motdColor": "",
            "motdHeading": "hi there!",
            "motdHeadingColor": "#ff3b3b",
        },
        {
            "type": "llamacpp",
            "urlSuffix": "vicky65",
            "label": "vicky-65b-experimental",
            "isEnabled": True,
            "deviceName": "cpu",
            "protocol": "http",
            "serverAddress": "192.168.1.10",
            "port": "64222",
            "requiresAccessToken": False,
            "maxTokens": 2060,
            "userRole": "Human",
            "assistantRole": "Assistant",
            "stopToken": "</s>",
            "separator": " \n",
            "systemPrompt": "",
            "motd": "this is the 65B Vicky model running in slow mode",
            "motdColor": "",
            "motdHeading": "hi there!",
            "motdHeadingColor": "#ff3b3b",
        },
    ]
    wasCreated = False
    if not os.path.isfile(json_filepath):
        with open(json_filepath, "w") as f:
            json.dump(default_data, f)
        wasCreated = True

    if wasCreated:
        print("Created default endpoints.json config file...")
        endpointList = default_data
    else:
        with open(json_filepath, "r") as f:
            data = json.load(f)

        required_properties = {
            "type",
            "urlSuffix",
            "label",
            "isEnabled",
            "deviceName",
            "protocol",
            "serverAddress",
            "port",
            "requiresAccessToken",
            "maxTokens",
            "userRole",
            "assistantRole",
            "stopToken",
            "separator",
            "systemPrompt",
            "motd",
            "motdColor",
            "motdHeading",
            "motdHeadingColor",
        }
        valid_types = {"llamacpp", "transformers", "openai"}
        endpointList = []

        for item in data:
            if item.get("type") not in valid_types:
                print(f"Invalid endpoint type value: {item.get('type')}")
                continue
            if not required_properties.issubset(item.keys()):
                print(f"Missing properties in endpoint item: {item}")
                continue
            endpointList.append(item)

    if shouldOutputSettings:
        for endpoint in endpointList:
            printDictAsTable(
                remove_keys_from_dict(endpoint, ["systemPrompt"]),
                f"Registered endpoint /'{endpoint['urlSuffix']}'",
            )

    return endpointList
