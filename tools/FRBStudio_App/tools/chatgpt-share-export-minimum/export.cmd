@echo off
setlocal
cd /d "%~dp0"

pause

if "%~1"=="" (
  echo Usage: export.cmd "https://chatgpt.com/share/6a7ab34d-f468-83e8-a1cb-fd10519a5dff" [output-dir]
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