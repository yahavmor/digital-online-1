@echo off
REM Drag one or more videos onto this file. Outputs appear in workspace\output.
cd /d "%~dp0"
if "%~1"=="" (echo Drag video files onto this icon. & pause & exit /b)
call factory.bat process --archive %*
start "" "workspace\output"
pause
