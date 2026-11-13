@echo off
setlocal EnableExtensions

rem Resolve FRBStudio_App root from this BAT: tools\FileTree\..\..
for %%I in ("%~dp0..\..") do set "APP_ROOT=%%~fI"

if not exist "%APP_ROOT%\wwwroot\index.html" (
  echo ERROR: FRBStudio_App root could not be resolved: "%APP_ROOT%"
  pause
  exit /b 1
)

pushd "%APP_ROOT%" || exit /b 1
tree /F /A > "%APP_ROOT%\file_list_Tree.txt"
set "EXIT_CODE=%ERRORLEVEL%"
popd

if not "%EXIT_CODE%"=="0" (
  echo ERROR: tree command failed. exit_code=%EXIT_CODE%
  pause
  exit /b %EXIT_CODE%
)

echo Wrote: "%APP_ROOT%\file_list_Tree.txt"
pause
exit /b 0
