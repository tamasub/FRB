@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
node "%SCRIPT_DIR%build_entry_result_rows_v0_1.cjs" %*
if errorlevel 1 (
  echo.
  echo Entry Result Rows の生成に失敗しました。
  exit /b 1
)
endlocal
