@echo off
setlocal
rem FRB Launch: user settings + diagnostics backup sample.
rem Output: %%LOCALAPPDATA%%\FRBLaunch\_Backups\FRBLaunch_Backup_YYYYMMDD_HHMMSS.zip
rem No source files are changed or deleted.

rem The PowerShell script resolves LaunchHome from its own script directory.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\Backup-FrbLaunch.ps1"
set "BACKUP_EXIT_CODE=%ERRORLEVEL%"
if not "%BACKUP_EXIT_CODE%"=="0" (
    echo.
    echo [ERROR] FRB Launch backup failed. See the message above.
) else (
    echo.
    echo [OK] FRB Launch backup finished.
)
echo.

exit /b %BACKUP_EXIT_CODE%


