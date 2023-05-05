# Tanglebox Model Runner

A host-it-yourself language model inferencing / chat bot platform.

## Features

vicuna-7b-v1.1 fits in 8GB VRAM on a 3000 or newer nvidia card, and vicuna-13b-v1.1 fits in 16GB!

### Back End

- [REST API endpoint](#REST-Endpoint)
- Pure websocket endpoint
- Web server for UI
- Model inferencing using either pytorch / HF transformers or pyllama.cpp
- On the fly 8bit quantization to fit large models in minimal VRAM

### Front End

- Markdown support
- Reponsive UI
- Response streaming using websockets

See [development](#development) for future features or way to contribute

Tested on windows 10, python-3.8.0

## Installation

Note: Selecting the CUDA option still allows for CPU-based inferencing

### With conda, Windows

- Run `install_win64_with_conda.bat`

This script will install miniconda3 for you if not already installed

### Without conda, Windows

- Install `python-3.8.0` and VS2019 as above, if needed
- Make sure pip is up to date: `python -m pip install --upgrade pip`
- With CUDA acceleration:
  - use `pip install -r requirements-cuda.txt`
- CPU only:
  - use `pip install -r requirements-cpu`

### Other OSs including 32-bit Windows

I've included the .whl for HuggingFace transformers for 64-bit Windows to greatly simplify the installation, which usually requires a c++ compiler to build during install. If you're not running Windows or for some reason are not on 64-bit, you'll need VS2019 or another appropriate c++ compiler installed - maybe try `conda install compilers -c conda-forge`.

- With conda
  - Install miniconda3
  - In a command line: `conda create -n tanglebox python=3.8.0`
  - Then: `conda activate tanglebox`
- Without conda
  - Install python 3.8.0
- Make sure pip is up to date: `python -m pip install --upgrade pip`
- To install transformers `pip install -r requirements-transformers.txt`
- With CUDA acceleration:
  - use `pip install -r requirements-cuda.txt`
- CPU only:
  - use `pip install -r requirements-cpu`

[troubleshooting](#troubleshooting)

## Usage

On windows, use: `run_with_conda.bat` or `run_native.bat`

Otherwise, just execute: `python main.py`

A `settings.json` file will be generated:

```json
{
  "conversationTemplate": "vicky", // see conversationTemplates.py
  "device": "cuda", // "cuda" | "cpu" | "cpu-ggml" | "mps"
  "enableApi": true, // enables REST API
  "enableModelDebugOutput": false,
  "enableWebLogOutput": false,
  "isApiTokensRequired": false, // requires API users to have a token
  "maintenanceMode": false,
  "maxNewTokens": 512,
  "modelName": "models/vicuna-13b-v11", // see below
  "numberOfGpus": 1,
  "port": 8080,
  "temperature": 0.7,
  "use8BitCompression": true, // applies to CUDA device only
  "useSsl": false, // enable SSL connections
  "vRamGb": 13 // how much VRAM you have / wish to allow
}
```

- For ggml models, the `modelName` value should be the path to the **file**, eg `python main.py --model-path E:\models\ggml-vicuna-7b-1.1\ggml-vicuna-7b-1.1-q4_0.bin --cpu-ggml`

- For everything else, the value should be the path to the **folder** containing the model.

If the default settings.json needed modification, restart the process, then open your browser and navigate to `localhost:8080`

## Development

Use `cd client` and `npm install` to obtain dependencies, then `npm run dev` or `npm run build` to run or build the front end from source. Files from `build` are output to `client/dist` and must be copied to `server/static` and `server/templates` (for the index.html file) for them to be served by the server.

I'm primarily a front-end dev so contributions of any kind to back-end are greatly appreciated and welcomed. I would love to add support for more models, but know very little really about the scene. Right now I'm working on UI elements for image generation and other features - basically copying what gradio can do, but looking nice at the same time.

## Websockets

`main.py` should be fairly readable about what the different websocket messages do, but in summary, all WS communication is via the same WS, there's no other routes involved. Special tokens are used as follows:

```
All tokens are sent in the format <token><value> eg. "#-set-temperature-#0.7", or just <token> where no value is required

Source - Client
"#-set-temp-#" - float
"#-set-max-tokens-#" - int
"#-set-streaming-#" - string "true" | "false"
"#-get-config-#"
"#-delete-#"
"#-ping-#"

Source - Server
"#-set-#" - acknowledgement to any client "#-set-xxx-#" messages. ignored on front end
"#-delete-#" - acknowledgment conversation was deleted
"#-model-name-#" - string
"#-device-name-#" - string
"#-max-new-tokens-#" - int
"#-temperature-#" - float
"#a-c-k#" - acknowledgement to prompt input (tells front end to wait for a reply)
"#f-i-n#" - follows completion of the inferencing, even if there was an error (tells front end model has finished output)
"#-pong-#"
```

This should probably become a separate route for control messages, but the need has yet to arise for me and this prevents me having to put websocket instances onto a global object (or somesuch) to maintain context of the client session - KISS

## REST Endpoint

Send request to `localhost:8080/conversation`. POST with json or GET are both supported, but consider using POST if submitting long conversation history

### params:

    "token" string - required (if enabled)
    "userPrompt" string - required
    "systemPrompt" string - optional
    "conversationHistory" valid JSON array of arrays, see below - optional
    "temperature" float - optional
    "maxNewTokens" int - optional
    "shouldStreamResponse" string "true" or "false" - optional

If supplying a value for `conversationHistory`, the JSON structure should be an array of arrays containing role and message, eg. `[["Human","how do magnets work?"],["Assistant","They just do."]]`

Valid role values are string literals `"Human"` or `"AI"`. The actual role strings used by the model is dependent on the conversation template applied in settings.json. This way the user of the API is not concerned with any specifics of the model config in use by the server.

## Conversation Templates

Conversation templates exist in `conversationTemplates.py`. You can create new ones or customise what's there. Note the 'outputSeparator' - this was added because some models return a different character in place of the stop token from their output, while others don't. Eventually I'll code around this rather than requiring the user to specify

## Troubleshooting

For vicuna v1.1, ensure you use the correct templates for the stop token to work (eos should be </s>, for vicuna v0 it should be ###).

If using SSL (https) and stuck on 'connecting', check it's enabled in settings.json.

If you're on a 32-bit version of windows, or for whatever reason you see errors related to 'wheel build failed' or a .h file missing for sentencepiece, that means the included transformers .whl doesn't work for you, and you'll need to install VS2019 or an equivalent c++ compiler. See below.

I've not tested this repo on Linux or Mac, nor have I used it inside a venv. It works great in conda so I recommend that. Raise an issue if it doesn't work for you.

Double check you are using the right models with the right devices. For CUDA you should have pytorch_model .bin or .pth files, you can't run ggml quantized models on GPU. I've found I need 16GB of VRAM to run the vicuna-7b model on CUDA. Using 8bit compression means vicuna-13b-v11 now fits in 16GB VRAM, and 7b 1.1 in under 8GB

## Model links

- CUDA, fast: https://huggingface.co/eachadea/vicuna-7b-1.1
- GGML, cpu: https://huggingface.co/eachadea/ggml-vicuna-7b-1.1

## Windows VS2019 install

Grab the Visual Studio Build Tools 2019 installer.

- select "Desktop development with C++" under the main Workloads area

On the right hand side, the following optional modules should be selected:

- MSVC - VS 2019 C++ x64/x86 build tools (latest)
- Windows 10 SDK
- C++ CMake tools for Windows
- Testing tools core features - Build Tools
- C++ AddressSanitizer

Reboot

## Thanks

Thanks to LMSYS for providing the model that inspired me to want to build this, and for their python FastChat code I ripped off for the backend
