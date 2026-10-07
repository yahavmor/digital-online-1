@echo off
REM Launcher: factory.bat <command> [...]
cd /d "%~dp0"
if exist .venv\Scripts\python.exe (set PY=.venv\Scripts\python.exe) else (set PY=python)
%PY% -m factory %*
