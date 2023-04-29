# Tanglebox Model Runner

A host-it-yourself language model inferencing / chat bot platform.

## Features

vicuna-7b-v1.1 fits in 8GB VRAM on a 3000 or newer nvidia card, and vicuna-13b-v1.1 fits in 16GB!

### Back End

- REST API endpoint
- Pure websocket endpoint
- Web server for UI
- Model inferencing using either pytorch / HF transformers or pyllama.cpp for optimal performance
- On the fly 8bit quantization to fit large models in minimal VRAM

### Front End

- Markdown support
- Reponsive UI
- Response streaming using websockets

See [development](#development) for future features or way to contribute

Tested on windows 10, python-3.8.0

## Windows Installation Pre-requisites

Install Visual Studio Build Tools 2019. If you get errors during python install about wheel build fails or python

- select "Desktop development with C++" under the main Workloads area

On the right hand side, the following optional modules should be selected:

- MSVC - VS 2019 C++ x64/x86 build tools (latest)
- Windows 10 SDK
- C++ CMake tools for Windows
- Testing tools core features - Build Tools
- C++ AddressSanitizer

Reboot

## Installation

(without conda, on Windows)

- Install `python-3.8.0` and VS2019 as above, if needed
- Make sure pip is up to date: `python -m pip install --upgrade pip`
- Depending on whether you want to use an Nvidia GPU for inferencing:
  `pip install -r requirements-cuda.txt` or `pip install -r requirements-cpu.txt`

The CUDA option allows CPU, but the CPU-only install saves doing a ~2GB download.

(with conda)

- Install VS2019 as above, if needed, or perhaps: `conda install compilers -c conda-forge` (untested)

```
conda create -n tanglebox python=3.8.0
conda activate tanglebox
(for CPU only) pip install -r requirements-cpu.txt
(for CUDA) pip install -r requirements-cpu.txt
```

[troubleshooting](#troubleshooting)

## Usage

Execute: `python main.py`

a `settings.json` file will be generated:

```json
{
  "conversationTemplate": "vicky", // see conversationTemplates.py
  "device": "cuda", // "cuda" | "cpu" | "cpu-ggml" | "mps"
  "enableApi": true, // enables REST API
  "enableModelDebugOutput": false,
  "enableWebLogOutput": true,
  "isApiTokensRequired": false, // requires a token, which is specified in tokens.txt. Any value is accepted
  "maintenanceMode": false, // won't load a model, good for testing endpoints
  "maxNewTokens": 512,
  "modelName": "D:/AI/models/vicuna-13b-v11", // see below
  "numberOfGpus": 1,
  "port": 8080,
  "temperature": 0.7,
  "use8BitCompression": true, // applies to CUDA device only
  "useSsl": false, // enable SSL connections
  "vRamGb": 13
}
```

- For ggml models, the path should be to the **file**, eg `python main.py --model-path E:\models\ggml-vicuna-7b-1.1\ggml-vicuna-7b-1.1-q4_0.bin --cpu-ggml`

- For everything else, the path should be to the **folder** containing the model.

Then open your browser and navigate to `localhost:8080`

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

    "token" string - required if enabled
    "systemPrompt" string - optional
    "userPrompt" string
    "conversationHistory" JSON array of objects, each containing role, message eg. [{'Human','hi'}, {'AI','hello'}]
    "conversationTemplate" string - must exist on server, error returned if not
    "temperature" float
    "maxNewTokens" int
    "shouldStreamResponse" boolean (string "true" or "false")
    "messageSeparator" string - optional
    "outputSeparator" string - optional

## Conversation Templates

Conversation templates exist in `conversationTemplates.py`. You can create new ones or customise what's there. Note the 'outputSeparator' - this was added because some models return a different character in place of the stop token from their output, while others don't. Eventually I'll code around this rather than requiring the user to specify

## Troubleshooting

For vicuna v1.1, ensure you use the correct templates for the stop token to work (eos should be </s>, for vicuna v0 it should be ###).

If using SSL (https) and stuck on 'connecting', check it's enabled in settings.json.

For installation errors related to 'wheel build failed' or a .h file missing for sentencepiece, make sure to follow the VS2019 installation instructions above. The Win10 SDK is required for wheel builds on Windows 10. It's a shitty experience. If anyone knows how I can avoid this repo requiring it please tell me.

I've not tested this on Linux or Mac, nor have I used it inside a venv. It works great in conda so I recommend that. Raise an issue if it doesn't work for you.

Double check you are using the right models with the right devices. For CUDA you should have pytorch_model .bin or .pth files, you can't run ggml quantized models on GPU. I've found I need 16GB of VRAM to run the vicuna-7b model on CUDA. EDIT: vicuna-13b-v11 now fits in 16GB VRAM

- CUDA, fast: https://huggingface.co/eachadea/vicuna-7b-1.1
- GGML, cpu: https://huggingface.co/eachadea/ggml-vicuna-7b-1.1

## Thanks

Thanks to LMSYS for providing the model that inspired me to want to build this, and for their python FastChat code I ripped off for the backend
