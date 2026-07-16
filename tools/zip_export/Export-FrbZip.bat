@echo off
chcp 65001 >nul
setlocal
set "SCRIPT_DIR=%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%Export-FrbZip.ps1" %*
echo.
pause
