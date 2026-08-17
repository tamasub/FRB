@echo off
set "APP_ROOT=%~dp0"

pushd "%APP_ROOT%NativeShell"
dotnet publish -c Release
if errorlevel 1 exit /b %errorlevel%
popd

xcopy "%APP_ROOT%NativeShell\bin\Release\net48\publish\*" ^
      "%APP_ROOT%NativeShell_publish\" /E /I /Y

pause
