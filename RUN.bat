@echo off
set "CONDA_ROOT=Z:\AI\software\miniconda3"
set "ENV_NAME=ace-data_env"
set "WORKDIR=Z:\AI\projects\music\ace-data_tool"

start "ACE-STEP DATA-TOOL" cmd /k ""%CONDA_ROOT%\Scripts\activate.bat" %ENV_NAME% && cd /d %WORKDIR% && ace-data"