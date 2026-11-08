@echo off
setlocal
set "FRB_CACHE=%LOCALAPPDATA%\FRBLaunch\web_profile\cache"
if not exist "%FRB_CACHE%\" (
  echo No FRB Launch Web cache was found. Nothing to reset.
  pause
  exit /b 0
)
echo.
echo FRB Launch Web cache reset - backup/rename only
echo Close FRB Launch completely using its tray Exit menu FIRST.
echo Chrome and Studio profiles will NOT be touched.
echo.
choice /C YN /M "Have you closed FRB Launch and want to back up the cache"
if errorlevel 2 exit /b 1
powershell -NoProfile -ExecutionPolicy Bypass -Command "$p=Join-Path $env:LOCALAPPDATA 'FRBLaunch\web_profile\cache'; $n='cache_backup_'+(Get-Date -Format 'yyyyMMdd_HHmmss_fff'); Rename-Item -LiteralPath $p -NewName $n -ErrorAction Stop; Write-Output ('BACKED_UP_TO='+(Join-Path (Split-Path $p -Parent) $n))"
if errorlevel 1 (
  echo Failed. Check that FRB Launch and its WebEngine child processes are closed.
  pause
  exit /b 1
)
echo.
echo Done. The cache folder will be recreated next time a Web page is opened.
echo Original data, cookies, and logins have NOT been touched.
pause
