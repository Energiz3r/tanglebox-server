# Tanglebox WebUI

A web UI with support for llamacpp, transformers, and openAI LLMs.

## Demo

[VickyAI](https://model.tanglebox.ai)

## Features

- Markdown support
- Reponsive UI
- Conversation streaming using text/event-stream

See [development](#development) for future features or way to contribute

Tested on windows 10, python-3.11.0

## Installation

### With conda, Windows

- Run `install_win64_with_conda_server.bat` to set up the web UI
- Download the latest release of Llama.cpp and configure a server

The batch scripts will install miniconda3 for you if not already installed

### Without conda, Windows

- Install `python-3.11.0` and VS2019 as above, if needed
- Make sure pip is up to date: `python -m pip install --upgrade pip`
- For server:
  - use `pip install -r requirements-server.txt`

## Usage

On windows, use: `run_server_conda.bat`

Otherwise, just execute: `python server/main.py`

A `web_settings.json` file will be generated:

```json
{
  "defaultMaxTokens": 2060,
  "defaultTemperature": 0.7,
  "maintenanceMode": true,
  "maintenanceModeMessage": "Down for maintenance",
  "port": 8080,
  "enableTokenRules": false, // enables the feature for endpoints to require a token
  "useSsl": true,
  "webDebugOutput": true
}
```

The settings files are generated upon starting the server

## REST Endpoint

Send request to `localhost:8080/api/<endpoint name>`. POST with json body is supported

Note that the endpoints are configured in server/main.py - the above is an example. Configure as needed

request structure should be correct for the target endpoint
