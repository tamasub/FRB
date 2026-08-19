@echo off
setlocal
cd /d "%~dp0"

pause

if "%~1"=="" (
  echo Usage: export.cmd "https://chatgpt.com/share/6a8443f4-5d40-83ee-8325-fd7e218511cf" [output-dir]
  exit /b 2
)
pause

if "%~2"=="" (
  node export_chatgpt_share.mjs "%~1" "output"
) else (
  node export_chatgpt_share.mjs "%~1" "%~2"
)

exit /b %errorlevel%

pause