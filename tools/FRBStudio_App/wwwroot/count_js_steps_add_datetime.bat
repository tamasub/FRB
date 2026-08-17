@echo off
setlocal EnableExtensions

rem ===== count_js_steps runner =====
rem Output: <FRBStudio_App>\wwwroot\countstep\countstep_yyyyMMdd_HHmmss.txt

for %%I in ("%~dp0.") do set "ROOT=%%~fI"
set "EXCLUDE_DIR=js\lib\mermaid"

rem Prefer count_js_steps.py next to this BAT. Fallback to ROOT.
set "SCRIPT=%~dp0count_js_steps.py"
if not exist "%SCRIPT%" set "SCRIPT=%ROOT%\count_js_steps.py"

if not exist "%ROOT%\" (
  echo ERROR: target folder not found: "%ROOT%"
  pause
  exit /b 1
)

if not exist "%SCRIPT%" (
  echo ERROR: count_js_steps.py not found: "%SCRIPT%"
  pause
  exit /b 1
)

rem Build timestamp without FOR loop to avoid %% variable trouble.
set "DATE_PART=%DATE:/=%"
set "DATE_PART=%DATE_PART:-=%"
set "DATE_PART=%DATE_PART:.=%"
set "DATE_PART=%DATE_PART: =%"

set "TIME_PART=%TIME::=%"
set "TIME_PART=%TIME_PART:.=%"
set "TIME_PART=%TIME_PART: =0%"
set "TIME_PART=%TIME_PART:~0,6%"

set "TS=%DATE_PART%_%TIME_PART%"
set "OUT_DIR=%ROOT%\countstep"
set "OUT_FILE=%OUT_DIR%\countstep_%TS%.txt"

if not exist "%OUT_DIR%\" mkdir "%OUT_DIR%"

> "%OUT_FILE%" echo count_js_steps run_datetime: %DATE% %TIME%
>> "%OUT_FILE%" echo target_folder: %ROOT%
>> "%OUT_FILE%" echo exclude_folder: %EXCLUDE_DIR%
>> "%OUT_FILE%" echo script: %SCRIPT%
>> "%OUT_FILE%" echo.

python "%SCRIPT%" "%ROOT%" --exclude-dir "%EXCLUDE_DIR%" >> "%OUT_FILE%" 2>&1


if errorlevel 1 (
  >> "%OUT_FILE%" echo.
  >> "%OUT_FILE%" echo ERROR: count_js_steps.py failed.
  echo ERROR: count_js_steps.py failed. See: "%OUT_FILE%"
) else (
  echo Wrote: "%OUT_FILE%"
)

pause
