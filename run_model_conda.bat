@echo off
TITLE VickyModel
set CONDA_PATH="%UserProfile%\miniconda3"
set CONDA_ENV=tanglebox-model
set SCRIPT_PATH=model\main.py
:start
call %CONDA_PATH%\Scripts\activate %CONDA_ENV%
python %SCRIPT_PATH%
goto start