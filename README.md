# Tanglebox Model Runner

![preview](https://i.imgur.com/MNqyb0U.png)

# Features

- Markdown support
- Reponsive UI
- Streaming / realtime output (toggleable)
- Backends using pytorch for CUDA/mps/CPU, and llama.cpp for CPU

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

Edit and run `run_server.bat`

or

`python main.py --model-path /path/to/model/modelName`

eg

`python main.py --model-path E:/models/vicuna-13b`

For ggml models, the path should be to the **file**, eg `python main.py --model-path E:\models\ggml-vicuna-7b-1.1\ggml-vicuna-7b-1.1-q4_0.bin --cpu-ggml`

For everything else, the path should be to the **folder** containing the model.

## Parameters

Using `--device cpu-ggml` will cause tanglebox to use pyllamacpp backend for inferencing. This is preferred / faster when using CPU.

```
--temperature <float> default=0.7
--max-new-tokens <integer> default=512
--device "cuda" | "cpu" | "cpu-ggml" | "mps" default=cuda
--port <integer> default=8080
--conv-template <string> default=vicuna1.1 see conversationTemplates.py for templating and instructions
--num-gpus <integer> default=1
--debug
--ssl enable SSL mode
--load-8bit - haven't been able to get this working but have copied LMsys' code verbatim so beats me why
--eos - allow specifying custom eos token
--vram-gb - GB of vram you have available default=13
```

Then open your browser and navigate to `localhost:8080` (or whatever port you specified)

## Development

Use `cd client` and `npm install` to obtain dependencies, then `npm run dev` or `npm run build` to run or build the front end from source. Files from `build` are output to `client/dist` and must be copied to `server/static` and `server/templates` (for the index.html file) for them to be served by the server.

I'm primarily a front-end dev so contributions of any kind to back-end are greatly appreciated and welcomed. I would love to add support for more models, but know very little really about the scene. Right now I'm working on UI elements for image generation and other features - basically copying what gradio can do, but looking nice at the same time.

`main.py` should be fairly readable about what the different websocket messages do, but in summary, all communication is via the same websocket. Special tokens are used as follows:

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

## Troubleshooting

For vicuna v1.1, ensure you use `--eos` for correct prompting.

If using SSL (https) and stuck on 'connecting', pass the `--ssl` switch.

For installation errors related to 'wheel build failed' or a .h file missing for sentencepiece, make sure to follow the VS2019 installation instructions above. The Win10 SDK is required for wheel builds on Windows 10.

I've not tested this on Linux or Mac, nor have I used it inside Conda or a venv. Raise an issue if it doesn't work for you.

Double check you are using the right models with the right devices. For CUDA you should have pytorch_model .bin or .pth files, you can't run ggml quantized models on GPU. I've found I need 16GB of VRAM to run the vicuna-7b model on CUDA.

- CUDA, fast: https://huggingface.co/eachadea/vicuna-7b-1.1
- GGML, cpu: https://huggingface.co/eachadea/ggml-vicuna-7b-1.1
