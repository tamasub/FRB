@echo off
setlocal
cd /d "%~dp0"
call "%~dp0make_FRB_Launch_Studio_bundle.bat" %*
exit /b %ERRORLEVEL%
