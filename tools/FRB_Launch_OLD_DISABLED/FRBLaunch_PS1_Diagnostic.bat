@echo off
setlocal EnableExtensions DisableDelayedExpansion
title FRB Launch - PowerShell Diagnostic
cd /d "%~dp0"
echo ============================================================
echo FRB Launch - PS1 diagnostic
 echo ============================================================
echo.
set "TEST_SCRIPT=%~1"
if not defined TEST_SCRIPT set "TEST_SCRIPT=%~dp0FRBLaunch_PS1_Diagnostic_Sample.ps1"
if not exist "%TEST_SCRIPT%" (
  echo [ERROR] Script not found:
  echo   "%TEST_SCRIPT%"
  echo.
  echo Drag and drop a .ps1 file onto this .cmd to test it,
  echo or put FRBLaunch_PS1_Diagnostic_Sample.ps1 alongside this .cmd.
  echo.
  pause
  exit /b 2
)
echo [TARGET] "%TEST_SCRIPT%"
echo.
echo [1] PowerShell version and executable
where powershell.exe
powershell.exe -NoProfile -Command "$PSVersionTable.PSVersion.ToString()"
echo.
echo [2] Execution policy by scope
powershell.exe -NoProfile -Command "Get-ExecutionPolicy -List | Format-Table -AutoSize | Out-String -Width 160 | Write-Host"
echo.
echo [3] Running the same command used by FRB Launch
 echo PowerShell will use its existing execution policy.
 echo ------------------------------------------------------------
powershell.exe -NoProfile -File "%TEST_SCRIPT%"
set "RESULT=%ERRORLEVEL%"
echo ------------------------------------------------------------
echo [EXIT CODE] %RESULT%
if not "%RESULT%"=="0" (
  echo [FAILED] The error above explains why the script did not run.
  echo Note: PID started does NOT mean the script succeeded.
) else (
  echo [EXIT CODE 0] Script returned normally; inspect its own results.
)
echo.
echo Please capture this window and share the output.
pause
exit /b %RESULT%
