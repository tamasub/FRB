@echo off
setlocal
cd /d "%~dp0"

echo [1/2] npm package install...
call npm install
if errorlevel 1 goto :error

echo [2/2] Playwright Chromium install...
call npx playwright install chromium
if errorlevel 1 goto :error

echo.
echo Setup completed.
exit /b 0

:error
echo.
echo Setup failed. errorlevel=%errorlevel%
exit /b %errorlevel%
