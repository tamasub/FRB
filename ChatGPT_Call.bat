@echo off
chcp 65001 > nul

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0ChatGPT_Call.ps1"

echo.
pause
