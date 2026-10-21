@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
 echo Run build_windows.bat first.
 pause
 exit /b 1
)
.venv\Scripts\python.exe src\app.py
if errorlevel 1 pause
