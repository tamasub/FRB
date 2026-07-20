@echo off
setlocal
cd /d "%~dp0"

if "%~1"=="" (
  echo Usage: export.cmd "https://chatgpt.com/share/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" [output-dir]
  exit /b 2
)

if "%~2"=="" (
  node export_chatgpt_share.mjs "%~1" "output"
) else (
  node export_chatgpt_share.mjs "%~1" "%~2"
)

exit /b %errorlevel%
