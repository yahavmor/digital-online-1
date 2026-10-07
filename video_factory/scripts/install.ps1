# Video Factory installer — Windows (PowerShell).  Right-click > "Run with PowerShell"
#   .\scripts\install.ps1 -NoModels   to skip the speech models (download on first use instead)
param([switch]$NoModels)
$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

Write-Host "1/4 FFmpeg" -ForegroundColor Cyan
if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        winget install --id Gyan.FFmpeg -e --accept-source-agreements --accept-package-agreements
        Write-Host "FFmpeg installed. Close and reopen PowerShell, then run this script again." -ForegroundColor Yellow
        exit 0
    } else {
        Write-Host "Install FFmpeg (full build) from https://www.gyan.dev/ffmpeg/builds/ and add it to PATH." -ForegroundColor Red
        exit 1
    }
}
ffmpeg -hide_banner -version | Select-Object -First 1

Write-Host "2/4 Python environment" -ForegroundColor Cyan
if (Get-Command py -ErrorAction SilentlyContinue) { $py = "py" } else { $py = "python" }   # PS 5.1-safe
if (-not (Test-Path .venv)) { & $py -m venv .venv }
& .\.venv\Scripts\python.exe -m pip install -q --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -q -r requirements.txt

Write-Host "3/4 Assets" -ForegroundColor Cyan
if ($NoModels) { & .\.venv\Scripts\python.exe -m factory setup --models none }
else { & .\.venv\Scripts\python.exe -m factory setup }

Write-Host "4/4 Check" -ForegroundColor Cyan
& .\.venv\Scripts\python.exe -m factory doctor
Write-Host "`nDone. Drag videos onto DROP_VIDEOS_HERE.bat, or run START_WATCH.bat and drop files into workspace\input." -ForegroundColor Green
