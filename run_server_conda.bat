@echo off
TITLE VickyWebServer
set CONDA_PATH="%UserProfile%\miniconda3"
set CONDA_ENV=tanglebox-server
set SCRIPT_PATH=server\main.py
:start
call %CONDA_PATH%\Scripts\activate %CONDA_ENV%
python %SCRIPT_PATH%
goto start