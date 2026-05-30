@echo off
setlocal enabledelayedexpansion

rem ==================================================
rem FRB ESP32 Firmware Installer
rem ASCII only version for Windows cmd safety
rem ==================================================

cd /d "%~dp0"

set "TOOL=%~dp0tools\esptool.exe"
set "FW=%~dp0firmware"

set "BOOTLOADER=%FW%\bootloader.bin"
set "PARTITIONS=%FW%\partitions.bin"
set "BOOTAPP=%FW%\boot_app0.bin"
set "APP=%FW%\firmware.bin"
set "SPIFFS=%FW%\spiffs.bin"

echo.
echo ==========================================
echo  FRB ESP32 Firmware Installer
echo ==========================================
echo.
echo Step 1:
echo   Connect ESP32 to USB.
echo.
echo Step 2:
echo   Check COM port in Device Manager.
echo   Example: COM3, COM5, COM12
echo.
echo If you input only number like 3, it will be treated as COM3.
echo.

set /p PORT=Input COM port: 

rem If user enters only number, convert to COM number
echo %PORT% | findstr /r /i "^COM[0-9][0-9]*$" >nul
if errorlevel 1 (
  echo %PORT% | findstr /r "^[0-9][0-9]*$" >nul
  if not errorlevel 1 (
    set "PORT=COM%PORT%"
  )
)

echo.
echo Selected port: %PORT%
echo.

if not exist "%TOOL%" (
  echo [ERROR] esptool.exe not found.
  echo Expected:
  echo   %TOOL%
  echo.
  echo Please copy esptool.exe into tools folder.
  pause
  exit /b 1
)

if not exist "%BOOTLOADER%" (
  echo [ERROR] bootloader.bin not found.
  echo Expected:
  echo   %BOOTLOADER%
  pause
  exit /b 1
)

if not exist "%PARTITIONS%" (
  echo [ERROR] partitions.bin not found.
  echo Expected:
  echo   %PARTITIONS%
  pause
  exit /b 1
)

if not exist "%APP%" (
  echo [ERROR] firmware.bin not found.
  echo Expected:
  echo   %APP%
  pause
  exit /b 1
)

echo Files:
echo   esptool    : %TOOL%
echo   bootloader : %BOOTLOADER%
echo   partitions : %PARTITIONS%
echo   app        : %APP%

if exist "%BOOTAPP%" (
  echo   boot_app0  : %BOOTAPP%
) else (
  echo   boot_app0  : not found - skip
)

if exist "%SPIFFS%" (
  echo   spiffs     : %SPIFFS%
) else (
  echo   spiffs     : not found - skip
)

echo.
echo Start flashing...
echo.

rem ==================================================
rem Flash command
rem Standard Arduino ESP32 addresses:
rem   bootloader  0x1000
rem   partitions  0x8000
rem   boot_app0   0xE000
rem   app         0x10000
rem   spiffs      0x290000  <- depends on partition table
rem ==================================================

if exist "%BOOTAPP%" (
  if exist "%SPIFFS%" (
    "%TOOL%" --chip esp32 --port "%PORT%" --baud 921600 --before default_reset --after hard_reset write_flash -z ^
      0x1000 "%BOOTLOADER%" ^
      0x8000 "%PARTITIONS%" ^
      0xE000 "%BOOTAPP%" ^
      0x10000 "%APP%" ^
      0x290000 "%SPIFFS%"
  ) else (
    "%TOOL%" --chip esp32 --port "%PORT%" --baud 921600 --before default_reset --after hard_reset write_flash -z ^
      0x1000 "%BOOTLOADER%" ^
      0x8000 "%PARTITIONS%" ^
      0xE000 "%BOOTAPP%" ^
      0x10000 "%APP%"
  )
) else (
  if exist "%SPIFFS%" (
    "%TOOL%" --chip esp32 --port "%PORT%" --baud 921600 --before default_reset --after hard_reset write_flash -z ^
      0x1000 "%BOOTLOADER%" ^
      0x8000 "%PARTITIONS%" ^
      0x10000 "%APP%" ^
      0x290000 "%SPIFFS%"
  ) else (
    "%TOOL%" --chip esp32 --port "%PORT%" --baud 921600 --before default_reset --after hard_reset write_flash -z ^
      0x1000 "%BOOTLOADER%" ^
      0x8000 "%PARTITIONS%" ^
      0x10000 "%APP%"
  )
)

if errorlevel 1 (
  echo.
  echo [ERROR] Flash failed.
  echo.
  echo Check:
  echo   1. COM port is correct.
  echo   2. USB cable supports data transfer.
  echo   3. ESP32 is connected.
  echo   4. Try holding BOOT button while flashing starts.
  echo   5. Try lower baud rate 115200 if needed.
  echo.
  pause
  exit /b 1
)

echo.
echo ==========================================
echo  Flash completed successfully!
echo ==========================================
echo.
pause
exit /b 0