@echo off
setlocal EnableExtensions

rem ============================================================
rem Copy FRBStudio publish root files to FRBStudio_App root
rem - Place this .bat in: FRBStudio_App
rem - Copies files only from FRBStudio publish root
rem - Excludes appsettings.json to protect local settings
rem - Does not copy folders
rem ============================================================

set "APP_ROOT=%~dp0"
set "SOURCE_DIR=%APP_ROOT%..\FRBStudio\bin\Release\net9.0-windows\win-x64\publish"

echo.
echo [FRBStudio] Publish root file copy
echo   Source : %SOURCE_DIR%
echo   Target : %APP_ROOT%
echo   Exclude: appsettings.json
echo.

if not exist "%SOURCE_DIR%\" (
  echo [ERROR] Source directory not found.
  echo         %SOURCE_DIR%
  echo.
  pause
  exit /b 1
)

pushd "%SOURCE_DIR%" >nul || (
  echo [ERROR] Failed to enter source directory.
  pause
  exit /b 1
)

set "COPY_COUNT=0"
set "SKIP_COUNT=0"

for %%F in (*) do (
  if /I "%%~nxF"=="appsettings.json" (
    echo [SKIP] %%~nxF
    set /a SKIP_COUNT+=1
  ) else (
    echo [COPY] %%~nxF
    copy /Y "%%~fF" "%APP_ROOT%%%~nxF" >nul
    if errorlevel 1 (
      echo [ERROR] Failed to copy: %%~nxF
      popd >nul
      pause
      exit /b 1
    )
    set /a COPY_COUNT+=1
  )
)

popd >nul

echo.
echo [DONE] Copied: %COPY_COUNT% file(s), Skipped: %SKIP_COUNT% file(s)
echo.
pause
exit /b 0
