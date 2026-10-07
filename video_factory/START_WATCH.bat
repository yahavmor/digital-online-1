@echo off
REM Double-click: opens the input folder and starts the watcher. Drop videos into the folder.
cd /d "%~dp0"
start "" "workspace\input"
call factory.bat watch
pause
