@echo off
setlocal
set "LOG=%LOCALAPPDATA%\FRBLaunch\launch.log"
if not exist "%LOG%" (
  echo launch.log was not found at: "%LOG%"
  echo Start FRBLaunch.exe and retry.
  pause
  exit /b 1
)
start "" notepad.exe "%LOG%"
