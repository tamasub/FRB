@echo off
setlocal EnableExtensions

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\build\Build-NativeShell.ps1"
set "EXIT_CODE=%ERRORLEVEL%"

if not "%EXIT_CODE%"=="0" (
  echo.
  echo ERROR: NativeShell build failed. exit_code=%EXIT_CODE%
  pause
  exit /b %EXIT_CODE%
)



echo.
echo NativeShell build completed.
pause
exit /b 0
