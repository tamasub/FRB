@echo off
setlocal EnableExtensions DisableDelayedExpansion
rem Portable v0.2, patched EXE resolves <its own dir>\Studio at runtime.
set "ROOT=%~dp0"
if not exist "%ROOT%Studio\NativeShell\_publish\FRBStudio.NativeShell.exe" (
  echo [ERROR] Studio executable missing in package: "%ROOT%Studio\NativeShell\_publish\FRBStudio.NativeShell.exe"
  pause
  exit /b 1
)
cd /d "%ROOT%"
start "" "%ROOT%FRBLaunch.exe"
if errorlevel 1 (
  echo [ERROR] Unable to start FRBLaunch.exe
  pause
  exit /b 1
)
exit /b 0
