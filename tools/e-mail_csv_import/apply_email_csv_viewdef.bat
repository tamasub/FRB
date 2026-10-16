@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
    py -3.14 "%~dp0apply_email_csv_viewdef.py"
) else (
    python "%~dp0apply_email_csv_viewdef.py"
)
if errorlevel 1 (
    echo.
    echo [FAILED] ViewDef update failed. No rebuild performed.
    pause
    exit /b 1
)
echo.
echo [OK] Now rebuild FRB Studio and FRB Launch.
pause
endlocal
