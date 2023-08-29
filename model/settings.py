from utils import printDictAsTable
import os
import json

def loadSettings():
    defaultSettings = {
        "port": 64223,
        "maintenanceMode": False,
        "maintenanceModeMessage": "This model is down for maintenance 🫠",
        "enableModelDebugOutput": False,
        "modelName": 'D:\\AI\\models\\vicuna-7b-v11',
        "modelAlias": 'vicky',
        "device": "cuda",
        "numberOfGpus": 1,
        "use8BitCompression": False,
        "vRamGb": 13,
    }
    didExist = True
    if not os.path.exists('model_settings.json'):
        didExist = False
        with open('model_settings.json', 'w') as file:
            json.dump(defaultSettings, file, indent=4, sort_keys=True)
    with open('model_settings.json', 'r') as file:
        settings = json.load(file)
    wasSettingMissingFromFile = False
    for key in defaultSettings:
        if key not in settings:
            wasSettingMissingFromFile = True
            print(f"Missing key: {key}")
            settings[key] = defaultSettings[key]
    if wasSettingMissingFromFile:
        with open('model_settings.json', 'w') as file:
            json.dump(settings, file, indent=4, sort_keys=True)
            print("Updated missing settings in model_settings.json...")
    printDictAsTable(settings, "Loaded config from model_settings.json:" if didExist else "Created config file model_settings.json:", ["Setting", "Value"])
    return settings