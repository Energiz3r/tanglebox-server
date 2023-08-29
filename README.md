# Tanglebox Model Runner

A host-it-yourself language model inferencing / chat bot platform.

## Features

vicuna-7b-v1.1 fits in 8GB VRAM on a 3000 or newer nvidia card, and vicuna-13b-v1.1 fits in 16GB!

### Back End

- [REST API endpoint](#REST-Endpoint)
- Web server for UI
- Model inferencing using either HF transformers or pyllama.cpp
- On the fly 8bit quantization to fit large models in minimal VRAM

### Front End

- Markdown support
- Reponsive UI
- Conversation streaming using text/event-stream

See [development](#development) for future features or way to contribute

Tested on windows 10, python-3.11.0

## Installation

Note: Selecting the CUDA option still allows for CPU-based inferencing

### With conda, Windows

- Run `install_win64_with_conda_server.bat` to set up the web UI
- Run `install_win64_with_conda_model.bat` to set up an HF Transformers model instance, or
- Download the latest release of Llama.cpp and configure a server

The batch scripts will install miniconda3 for you if not already installed

### Without conda, Windows

- Install `python-3.11.0` and VS2019 as above, if needed
- Make sure pip is up to date: `python -m pip install --upgrade pip`
- For server:
  - use `pip install -r requirements-server.txt`
- With CUDA acceleration:
  - use `pip install -r requirements-cuda.txt`
- CPU only:
  - use `pip install -r requirements-cpu`

### Other OSs including 32-bit Windows

I've included the .whl for HuggingFace transformers for 64-bit Windows to greatly simplify the installation, which usually requires a c++ compiler to build during install. If you're not running Windows or for some reason are not on 64-bit, you'll need VS2019 or another appropriate c++ compiler installed - maybe try `conda install compilers -c conda-forge`.

- With conda
  - Install miniconda3
  - In a command line: `conda create -n tanglebox-model python=3.11.0`
  - Then: `conda activate tanglebox-model`
- Without conda
  - Install python 3.11.0
- Make sure pip is up to date: `python -m pip install --upgrade pip`
- To install transformers `pip install -r requirements-transformers.txt`
- With CUDA acceleration:
  - use `pip install -r requirements-cuda.txt`
- CPU only:
  - use `pip install -r requirements-cpu`

- For the server
  - In a command line: `conda create -n tanglebox-server python=3.11.0`
  - Then: `conda activate tanglebox-server`
  - Then: `pip install -r requirements-server`

[troubleshooting](#troubleshooting)

## Usage

On windows, use: `run_server_conda.bat` and/or `run_model_conda.bat`

Otherwise, just execute: `python server/main.py` and `python model/main.py`

A `web_settings.json` file will be generated:

```json
{
    "defaultMaxTokens": 2060,
    "defaultTemperature": 0.7,
    "maintenanceMode": true,
    "maintenanceModeMessage": "Down for maintenance",
    "port": 8080,
    "shouldRequireToken": false, // requires API users to have a token
    "useSsl": true,
    "webDebugOutput": true
}
```

and a `model_settings.json`:

```json

{
  "port": 64223,
  "maintenanceMode": false,
  "maintenanceModeMessage": "This model is down for maintenance 🫠",
  "enableModelDebugOutput": false,
  "modelName": "models/vicuna-7b-v11",
  "modelAlias": "vicuna-7b",
  "device": "cuda", // "cuda" | "cpu" | "mps"
  "numberOfGpus": 1,
  "use8BitCompression": false, // applies to CUDA device only
  "vRamGb": 13, // how much VRAM you have / wish to allow
}
```

- The value of "modelName" should be the path to the **folder** containing the model.

The settings files are generated upon starting the server

## Development

Use `cd client` and `npm install` to obtain dependencies, then `npm run dev` or `npm run build` to run or build the front end from source. Files from `build` are output to `client/dist` and must be copied to `server/static` and `server/templates` (for the index.html file) for them to be served by the server.

I'm primarily a front-end dev so contributions of any kind to back-end are greatly appreciated and welcomed. I would love to add support for more models, but know very little really about the scene. Right now I'm working on UI elements for image generation and other features - basically copying what gradio can do, but looking nice at the same time.

## REST Endpoint

Send request to `localhost:8080/conversation`. POST with json body is supported

Note that the endpoints are configured in server/main.py - the above is an example. Configure as needed

### params:

    prompt: "A chat between a curious user and an artificial intelligence assistant. The assistant gives helpful, detailed, and polite answers to the user's questions. USER: hi there \nASSISTANT:"
    n_predict: 2048
    temperature: 0.7
    stream: true

The above params are taken from llama.cpp's server and can be used interchangeably, however, note that other params used by llama.cpp are ignored by this model loader but can still be sent to the endpoint and will be passed on if it is a llama.cpp server. For reference, this is the full set of llama.cpp params:

    frequency_penalty: 0
    mirostat: 0
    mirostat_eta: 0.1
    mirostat_tau: 5
    n_predict: 2048
    presence_penalty: 0
    prompt: "Hi there\n\nHuman: \nAssistant:"
    repeat_last_n: 256
    repeat_penalty: 1.18
    stop: ["</s>", "Assistant:", "Human:"]
    stream: true
    temperature: 0.7
    tfs_z: 1
    top_k: 40
    top_p: 0.5
    typical_p: 1

## Troubleshooting

If you're on a 32-bit version of windows, or for whatever reason you see errors related to 'wheel build failed' or a .h file missing for sentencepiece, that means the included transformers .whl doesn't work for you, and you'll need to install VS2019 or an equivalent c++ compiler. See below.

I've not tested this repo on Linux or Mac, nor have I used it inside a venv. It works great in conda so I recommend that. Raise an issue if it doesn't work for you.

Double check you are using the right models with the right devices. For CUDA you should have pytorch_model .bin or .pth files. I've found I need 16GB of VRAM to run the vicuna-7b model on CUDA. Using 8bit compression means vicuna-13b-v11 now fits in 16GB VRAM, and 7b 1.1 in under 8GB

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
