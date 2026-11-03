@echo off
setlocal EnableExtensions
cd /d "%~dp0"
echo.
echo Lithos: generate TWO templates for distribution - never at startup
powershell.exe -NoProfile -STA -ExecutionPolicy Bypass -File "%~dp0ACCESS_SABLON_OLUSTUR.ps1"
if errorlevel 1 (
  echo.
  echo ACCESS TEMPLATE BUILD FAILED. Read Templates\ACCESS_SABLON_LOG.txt
  if /I not "%~1"=="--auto" pause
  exit /b 1
)
echo.
echo ACCESS TR AND EN TEMPLATES READY in Templates folder.
if /I not "%~1"=="--auto" pause
exit /b 0
