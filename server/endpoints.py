from utils import printDictAsTable, remove_keys_from_dict
import json
import os


def loadEndpoints(shouldOutputSettings=False):
    json_filepath = "endpoints.json"
    with open("endpoints_example.json", "r") as f:
        default_data = json.load(f)

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
            "isHidden",
            "deviceName",
            "protocol",
            "serverAddress",
            "port",
            "requiresAccessToken",
            "maxTokens",
            "systemPrompt",
            "promptType",
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
                remove_keys_from_dict(endpoint, ["systemPrompt", "motd", "motdColor", "motdHeadingColor", "maxTokens"]),
                f"Registered endpoint /'{endpoint['urlSuffix']}'",
                ["Key", "Value"],
                not endpoint["isEnabled"]
            )

    return endpointList
