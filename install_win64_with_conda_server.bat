@echo off

set CONDA_ENV=tanglebox-server
set ORIGDIR="%CD%"
set MINICONDAPATH=%USERPROFILE%\Miniconda3
set CONDAEXE=%TEMP%\%RANDOM%-%RANDOM%-%RANDOM%-%RANDOM%-condainstall.exe

where conda >nul 2>nul
if %ERRORLEVEL% EQU 0 goto CONDAFOUND

:INSTALLCONDA

echo Downloading Miniconda3 (This will take while, please wait)...
powershell -Command "(New-Object Net.WebClient).DownloadFile('https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe', '%CONDAEXE%')" >nul 2>nul
if errorlevel 1 goto CONDAERROR

echo Installing Miniconda3 (This will also take a while, please wait)...
start /wait /min "Installing Miniconda3..." "%CONDAEXE%" /InstallationType=JustMe /S /D="%MINICONDAPATH%"
del "%CONDAEXE%"
if not exist "%MINICONDAPATH%\" (goto CONDAERROR)

"%MINICONDAPATH%\Scripts\conda.exe" init
if errorlevel 1 goto CONDAERROR

echo Miniconda3 has been installed!
goto CONDASUCCESS

:CONDAERROR
echo Miniconda3 install failed!
pause
exit /B 1

:CONDAFOUND
echo Conda is already installed!
goto CONDASUCCESS

:CONDASUCCESS
echo Creating conda environment...
"%MINICONDAPATH%\Scripts\conda.exe" create -n %CONDA_ENV% python=3.11.4
call "%MINICONDAPATH%\Scripts\activate" %CONDA_ENV%

pip3 install -r requirements-server.txt

:END
pause
exit /B 0