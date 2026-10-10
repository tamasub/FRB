@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" "%~dp0make_launch_zip.py"
) else (
  py -3 "%~dp0make_launch_zip.py"
)
if errorlevel 1 (
  echo ZIP creation failed. See the error above.
  pause
  exit /b 1
)
echo ZIP created successfully.
pause
