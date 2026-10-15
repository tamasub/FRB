@echo off
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\Set-LaunchStartup.ps1" -Remove
if errorlevel 1 echo Failed to disable startup.
pause
