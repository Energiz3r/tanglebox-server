@echo off
set CONDA_PATH="%UserProfile%\miniconda3"
set CONDA_ENV=tanglebox
set SCRIPT_PATH=E:\tanglebox-model-runner\server\main.py
:start
call %CONDA_PATH%\Scripts\activate %CONDA_ENV%
python %SCRIPT_PATH% --model-name D:\AI\models\vicuna-13b-v11 --conv-template vicky --temperature 0.8 --max-new-tokens 2048 --port 8080 --load-8bit
call %CONDA_PATH%\Scripts\deactivate
goto start