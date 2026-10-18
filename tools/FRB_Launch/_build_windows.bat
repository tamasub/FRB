@echo off
setlocal
cd /d "%~dp0"
echo [BUILD] Stopping FRBLaunch.exe if running...
taskkill /F /IM FRBLaunch.exe >nul 2>&1
rem Wait for process exit instead of trusting taskkill and a fixed two-second delay.
set /a _frb_wait=0
:wait_frb_exit
tasklist /FI "IMAGENAME eq FRBLaunch.exe" /NH | find /I "FRBLaunch.exe" >nul
if errorlevel 1 goto frb_process_stopped
set /a _frb_wait+=1
if %_frb_wait% GEQ 15 goto frb_process_stuck
timeout /t 1 /nobreak >nul
goto wait_frb_exit
:frb_process_stuck
echo [ERROR] FRBLaunch.exe did not exit after 15 seconds.
echo [ACTION] Exit the tray app or close the process in Task Manager, then rebuild.
goto fail
:frb_process_stopped
if exist .venv\Scripts\python.exe goto checkpython
py -3 -m venv .venv
if errorlevel 1 goto fail
:checkpython
.venv\Scripts\python.exe -c "import sys,struct; print('Build Python:',sys.version); print('Bits:',struct.calcsize('P')*8); sys.exit(0 if (3,10) <= sys.version_info[:2] < (3,15) and struct.calcsize('P')==8 else 1)"
if errorlevel 1 goto unsupported
.venv\Scripts\python.exe src\prepare_launch_home.py
if errorlevel 1 goto fail
rem The migration above must finish before any old dist is removed.
rem Stop before the long PyInstaller build if the previous DLLs are locked.
.venv\Scripts\python.exe src\build_output_preflight.py
if errorlevel 1 goto fail
if not "%FRB_ENV_REFRESH%"=="1" (
  .venv\Scripts\python.exe -m pip install --upgrade -r requirements.txt
  if errorlevel 1 goto fail
)
.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --windowed --onedir --name FRBLaunch --collect-all tzdata --icon "assets\frb_launch.ico" --add-data "assets;assets" src\app.py
if errorlevel 1 goto fail
xcopy /E /I /Y defs dist\FRBLaunch\defs
if errorlevel 1 goto fail
.venv\Scripts\python.exe src\prepare_launch_home.py --link
if errorlevel 1 goto fail
copy /Y README.md dist\FRBLaunch\README.md
if not "%FRB_ENV_REFRESH%"=="1" start "" explorer.exe "%~dp0dist\FRBLaunch"
echo Build complete: dist\FRBLaunch\FRBLaunch.exe
if not "%FRB_ENV_REFRESH%"=="1" pause
exit /b 0
:unsupported
echo This build requires standard 64-bit Python 3.10 to 3.14.
echo To choose Python 3.14 explicitly, create a fresh venv with: py -3.14 -m venv .venv
goto fail
:fail
echo Build failed. See the output above.
if not "%FRB_ENV_REFRESH%"=="1" pause
exit /b 1
