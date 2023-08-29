from utils import printDictAsTable
import os
import json


def loadWebSettings(shouldOutputSettings=False):
    webSettingsFilepath = "web_settings.json"
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
    if not os.path.exists(webSettingsFilepath):
        didExist = False
        with open(webSettingsFilepath, "w") as file:
            json.dump(defaultSettings, file, indent=4, sort_keys=True)
    with open(webSettingsFilepath, "r") as file:
        settings = json.load(file)
    wasSettingMissingFromFile = False
    for key in defaultSettings:
        if key not in settings:
            wasSettingMissingFromFile = True
            print(f"Missing key: {key}")
            settings[key] = defaultSettings[key]
    if wasSettingMissingFromFile:
        with open(webSettingsFilepath, "w") as file:
            json.dump(settings, file, indent=4, sort_keys=True)
            print(f"Updated missing settings in {webSettingsFilepath}...")
    if shouldOutputSettings:
        printDictAsTable(
            settings,
            f"Loaded config from {webSettingsFilepath}:"
            if didExist
            else f"Created config file {webSettingsFilepath}:",
            ["Setting", "Value"],
        )
    return settings
