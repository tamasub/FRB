@echo off
setlocal
set "TRACE_DIR=%LOCALAPPDATA%\FRBLaunch"
set "TRACE_PATH=%TRACE_DIR%\shuriken_trace.log"
set "RESULT=%~dp0FRBLaunch_ShuriTrace.zip"
if not exist "%TRACE_PATH%" (
  echo No shuriken trace yet. Start FRB Launch, use the wheel, and close Launch first.
  pause
  exit /b 1
)
echo Close FRB Launch before exporting the trace.
powershell -NoProfile -ExecutionPolicy Bypass -Command "$folder=Join-Path $env:LOCALAPPDATA 'FRBLaunch'; $items=@(Get-ChildItem -LiteralPath $folder -Filter 'shuriken_trace.log*' -File); if($items.Count -eq 0){exit 2}; $paths=@(foreach($item in $items){$item.FullName}); Compress-Archive -LiteralPath $paths -DestinationPath '%RESULT%' -Force"
if errorlevel 1 (
  echo Failed to export trace. Verify Launch is fully closed.
  pause
  exit /b 1
)
echo Created: %RESULT%
pause
