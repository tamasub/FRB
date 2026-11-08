@echo off
setlocal EnableExtensions DisableDelayedExpansion
chcp 65001 >nul
set "TOOL_DIR=%~dp0"
set "BUNDLE_ROOT=%~1"
if not defined BUNDLE_ROOT (
  echo.
  echo Existing incomplete bundle folder from the failed [4/5] step:
  echo e.g. F:\FRB\tools\frb_release_test_area\FRB_Bundle_Output\FRB_Launch
  set /p "BUNDLE_ROOT=Bundle folder: "
)
if not defined BUNDLE_ROOT (
  echo [ERROR] Bundle folder is required.
  pause
  exit /b 2
)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%TOOL_DIR%finish_FRB_bundle_after_error.ps1" -BundleRoot "%BUNDLE_ROOT%" -ToolDir "%TOOL_DIR%."
set "RESULT=%ERRORLEVEL%"
if not "%RESULT%"=="0" (
  echo [ERROR] Recovery failed. Exit code: %RESULT%
) else (
  echo [OK] You can now test the bundle without recopying the 212MB Launch dist.
)
pause
exit /b %RESULT%
