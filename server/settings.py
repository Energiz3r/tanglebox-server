from utils import printDictAsTable
import os
import json

def loadWebSettings(shouldOutputSettings = False):
    defaultSettings = {
        "defaultTemperature": 0.7,
        "defaultMaxTokens": 2060,
        "useSsl": False,
        "port": 8080,
        "webDebugOutput": False,
        "shouldRequireToken": False,
        "maintenanceMode": False,
        "maintenanceModeMessage": "Down for maintenance",
    }
    didExist = True
    if not os.path.exists('web_settings.json'):
        didExist = False
        with open('web_settings.json', 'w') as file:
            json.dump(defaultSettings, file, indent=4, sort_keys=True)
    with open('web_settings.json', 'r') as file:
        settings = json.load(file)
    wasSettingMissingFromFile = False
    for key in defaultSettings:
        if key not in settings:
            wasSettingMissingFromFile = True
            print(f"Missing key: {key}")
            settings[key] = defaultSettings[key]
    if wasSettingMissingFromFile:
        with open('web_settings.json', 'w') as file:
            json.dump(settings, file, indent=4, sort_keys=True)
            print("Updated missing settings in web_settings.json...")
    if shouldOutputSettings:
        printDictAsTable(settings, "Loaded config from web_settings.json:" if didExist else "Created config file settings.json:", ["Setting", "Value"])
    return settings