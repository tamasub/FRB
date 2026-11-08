@echo off
setlocal EnableExtensions DisableDelayedExpansion
chcp 65001 >nul
set "TOOL_DIR=%~dp0"

rem Usage:
rem   make_FRB_Launch_Studio_bundle.bat "REBUILT Launch project or dist folder" "Studio project or _publish folder" [output parent]
rem Input files are NEVER modified. A new output folder is created.
set "LAUNCH_SOURCE=%~1"
set "STUDIO_SOURCE=%~2"
set "OUTPUT_PARENT=%~3"

if not defined LAUNCH_SOURCE (
  echo.
  echo [1/3] FRB Launch source directory
  echo e.g. F:\FRB\tools\launch_app   or   F:\FRB\tools\launch_app\dist\FRBLaunch
  set /p "LAUNCH_SOURCE=Launch source: "
)
if not defined STUDIO_SOURCE (
  echo.
  echo [2/3] FRB Studio source directory
  echo e.g. F:\FRB\tools\FRBStudio_App
  set /p "STUDIO_SOURCE=Studio source: "
)
if not defined OUTPUT_PARENT (
  echo.
  echo [3/3] Output directory (press Enter for default)
  echo Default: %TOOL_DIR%FRB_Bundle_Output
  set /p "OUTPUT_PARENT=Output parent: "
)
if not defined OUTPUT_PARENT set "OUTPUT_PARENT=%TOOL_DIR%FRB_Bundle_Output"

if not defined LAUNCH_SOURCE goto input_error
if not defined STUDIO_SOURCE goto input_error

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%TOOL_DIR%assemble_FRB_Launch_Studio.ps1" -LaunchSource "%LAUNCH_SOURCE%" -StudioSource "%STUDIO_SOURCE%" -OutputParent "%OUTPUT_PARENT%" -ToolDir "%TOOL_DIR%."
set "RESULT=%ERRORLEVEL%"
echo.
if not "%RESULT%"=="0" (
  echo [ERROR] Bundle creation failed. Exit code: %RESULT%
  pause
  exit /b %RESULT%
)
echo [OK] Bundle directory assembled.
echo [NEXT] After fully exiting any running FRB Launch, start the relocated FRBLaunch.exe directly.
echo [WARNING] TEST BUNDLE ONLY - NEVER upload this build to Vector as-is.
pause
exit /b 0

:input_error
echo [ERROR] Source directories are required.
pause
exit /b 2
