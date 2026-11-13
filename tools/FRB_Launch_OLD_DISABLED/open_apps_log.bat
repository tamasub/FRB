@echo off
setlocal
set "LOG=%LOCALAPPDATA%\FRBLaunch\apps.log"
if not exist "%LOG%" (
  echo apps.log does not exist yet. Start FRB Launch and select "Update apps" from the tray menu.
  echo Expected location: "%LOG%"
  pause
  exit /b 1
)
start "" notepad.exe "%LOG%"
exit /b 0
