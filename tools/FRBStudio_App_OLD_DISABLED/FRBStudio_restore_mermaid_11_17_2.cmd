@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0FRBStudio_restore_mermaid_11_17_2.ps1"
set "RC=%ERRORLEVEL%"
echo.
if not "%RC%"=="0" echo Restore failed. Check the message above.
pause
exit /b %RC%
