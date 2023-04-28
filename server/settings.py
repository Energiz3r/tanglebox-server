from utils import printDictAsTable
import os
import json

def loadSettings():
    defaultSettings = {
        "modelName": 'D:\\AI\\models\\vicuna-7b-v11',
        "device": "cuda",
        "numberOfGpus": 1,
        "conversationTemplate": "vicuna0",
        "temperature": 0.7,
        "maxNewTokens": 512,
        "use8BitCompression": False,
        "vRamGb": 13,
        "useSsl": False,
        "port": 8080,
        "enableModelDebugOutput": False,
        "enableWebLogOutput": False,
        "maintenanceMode": False,
        "enableApi": True,
        "isApiTokensRequired": False
    }
    didExist = True
    if not os.path.exists('settings.json'):
        didExist = False
        with open('settings.json', 'w') as file:
            json.dump(defaultSettings, file, indent=4, sort_keys=True)
    with open('settings.json', 'r') as file:
        settings = json.load(file)
    wasSettingMissingFromFile = False
    for key in defaultSettings:
        if key not in settings:
            wasSettingMissingFromFile = True
            print(f"Missing key: {key}")
            settings[key] = defaultSettings[key]
    if wasSettingMissingFromFile:
        with open('settings.json', 'w') as file:
            json.dump(settings, file, indent=4, sort_keys=True)
            print("Updated missing settings in settings.json...")
    printDictAsTable(settings, "Loaded config from settings.json:" if didExist else "Created config file settings.json:", ["Setting", "Value"])
    return settings