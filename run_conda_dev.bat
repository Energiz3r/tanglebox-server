@echo off
set CONDA_PATH="%UserProfile%\miniconda3"
set CONDA_ENV=tanglebox
set SCRIPT_PATH=E:\tanglebox-model-runner\server\main.py

call %CONDA_PATH%\Scripts\activate %CONDA_ENV%
python %SCRIPT_PATH% --model-name E:/models/vicuna-7b-v11 --temperature 1.1 --max-new-tokens 2048 --port 8081
call %CONDA_PATH%\Scripts\deactivate

pause