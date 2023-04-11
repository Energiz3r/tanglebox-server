# tanglebox model runner

![logo](https://i.imgur.com/TlnVcbM.png)

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

`python -m pip install --upgrade pip`

Then, depending on whether you want to use an Nvidia GPU for inferencing:

`pip install -r requirements-cuda.txt`

or

`pip install -r requirements-cpu.txt`

The CUDA option allows CPU, but the CPU-only install saves doing a ~2GB download.

## Usage

`run_server.bat`

or

`python main.py --model-path /path/to/model/modelName`

eg

`python main.py --model-path E:/models/vicuna-13b`

(OPTIONAL)

```
--temperature <float> default=0.7
--max-new-tokens <integer> default=512
--device "cuda" | "cpu" | "cpu-gptq" | "mps" default=cuda
--port <integer> default=8080
--conv-template <string> default=v1
--num-gpus <integer> default=1
--debug
--load-8bit
```

Then open your browser and navigate to `localhost:8080` (or whatever port you specified)
