@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Export-FrbDocsArchive.ps1" %*
set "RESULT=%ERRORLEVEL%"
echo.
echo Exit code: %RESULT%
start "" F:\FRB\_archive

exit /b %RESULT%
