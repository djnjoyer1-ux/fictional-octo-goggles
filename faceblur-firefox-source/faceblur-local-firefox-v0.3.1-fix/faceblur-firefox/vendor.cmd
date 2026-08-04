@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0vendor.ps1"
if errorlevel 1 (
  echo.
  echo Download failed. Check your internet connection and try again.
  pause
  exit /b 1
)
echo.
echo Detector files installed. Reload FaceBlur in about:debugging.
pause
