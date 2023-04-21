@echo off
set CONDA_PATH="%UserProfile%\miniconda3"
set CONDA_ENV=tanglebox
set SCRIPT_PATH=E:\tanglebox-model-runner\server\main.py
:start
call %CONDA_PATH%\Scripts\activate %CONDA_ENV%
python %SCRIPT_PATH% --model-name E:\models\ggml-vicuna-7b-4bit\ggml-vicuna-7b-4bit-rev1.bin --conv-template vicuna0 --temperature 0.7 --max-new-tokens 2048 --port 8081 --device cpu-ggml
call %CONDA_PATH%\Scripts\deactivate
goto start

pause