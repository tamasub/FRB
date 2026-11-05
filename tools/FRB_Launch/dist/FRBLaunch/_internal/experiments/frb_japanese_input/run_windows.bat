@echo off
setlocal
cd /d "%~dp0"
if errorlevel 1 goto :bad_path

rem Prefer the FRB Launch virtual environment.
if exist "..\..\.venv\Scripts\python.exe" goto :run_launch_venv

rem Also support a local virtual environment.
if exist ".venv\Scripts\python.exe" goto :run_local_venv

rem Fall back to a Python installation on PATH.
where py >nul 2>nul
if not errorlevel 1 goto :run_py
where python >nul 2>nul
if not errorlevel 1 goto :run_python

echo [FRB Japanese Input] Python was not found.
echo Install Python or use the FRB Launch virtual environment.
pause
endlocal & exit /b 1

:run_launch_venv
"..\..\.venv\Scripts\python.exe" "frb_japanese_input.py"
goto :check_result

:run_local_venv
".venv\Scripts\python.exe" "frb_japanese_input.py"
goto :check_result

:run_py
py -3 "frb_japanese_input.py"
goto :check_result

:run_python
python "frb_japanese_input.py"
goto :check_result

:bad_path
echo [FRB Japanese Input] Cannot change to the application directory.
pause
endlocal & exit /b 1

:check_result
set "FRB_EXIT_CODE=%errorlevel%"
if "%FRB_EXIT_CODE%"=="0" goto :success

echo.
echo [FRB Japanese Input] Failed to start. Exit code: %FRB_EXIT_CODE%
echo If PySide6 is missing, run the following from this folder:
echo   python -m pip install -r requirements.txt
echo Or use the appropriate Python executable from your .venv.
pause
endlocal & exit /b %FRB_EXIT_CODE%

:success
endlocal & exit /b 0
