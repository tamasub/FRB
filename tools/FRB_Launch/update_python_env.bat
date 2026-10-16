@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo =======================================================
echo   FRB Launch - Python environment update / rebuild
echo =======================================================
echo.
echo [INFO] Checking installed Python 3.14 ...
py -3.14 -c "import struct,sys; print('Python:',sys.version.split()[0]); print('Path:',sys.executable); print('Bits:',struct.calcsize('P')*8); sys.exit(0 if sys.version_info[:2]==(3,14) and sys.version_info[:3]>=(3,14,8) and struct.calcsize('P')==8 else 1)"
if errorlevel 1 goto error

py -3.14 "%~dp0refresh_python_environment.py" %*
if errorlevel 1 goto error

echo.
echo [OK] Update completed. Review the build output above.
pause
exit /b 0

:error
echo.
echo [ERROR] Update failed. Check the error above.
echo Check that Python 3.14.8 or newer 64-bit is available via py -3.14.
pause
exit /b 1
