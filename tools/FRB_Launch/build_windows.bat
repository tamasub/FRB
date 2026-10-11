@echo off
setlocal
cd /d "%~dp0"
if exist .venv\Scripts\python.exe goto checkpython
py -3 -m venv .venv
if errorlevel 1 goto fail
:checkpython
.venv\Scripts\python.exe -c "import sys,struct; print('Build Python:',sys.version); print('Bits:',struct.calcsize('P')*8); sys.exit(0 if (3,10) <= sys.version_info[:2] < (3,15) and struct.calcsize('P')==8 else 1)"
if errorlevel 1 goto unsupported
.venv\Scripts\python.exe prepare_launch_home.py
if errorlevel 1 goto fail
.venv\Scripts\python.exe -m pip install --upgrade -r requirements.txt
if errorlevel 1 goto fail
.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --windowed --onedir --name FRBLaunch --collect-all tzdata app.py
if errorlevel 1 goto fail
xcopy /E /I /Y defs dist\FRBLaunch\defs
if errorlevel 1 goto fail
.venv\Scripts\python.exe prepare_launch_home.py --link
if errorlevel 1 goto fail
copy /Y README.md dist\FRBLaunch\README.md
start "" explorer.exe "%~dp0dist\FRBLaunch"
echo Build complete: dist\FRBLaunch\FRBLaunch.exe
pause
exit /b 0
:unsupported
echo This build requires standard 64-bit Python 3.10 to 3.14.
echo To choose Python 3.14 explicitly, create a fresh venv with: py -3.14 -m venv .venv
goto fail
:fail
echo Build failed. See the output above.
pause
exit /b 1
