@echo off
setlocal EnableExtensions
cd /d "%~dp0"
echo.
echo [Lithos clean] Create Windows installer from fresh portable files
if not exist "dist\Lithos_v1_0_2\Lithos_v1_0_2.exe" (
  echo Portable build missing. Run 02_PORTABLE_OLUSTUR.bat first.
  if /I not "%~1"=="--auto" pause
  exit /b 1
)
if not exist "dist\Lithos_v1_0_2\GUI_EXE_TESTI.txt" (
  echo MISSING EXE STARTUP TEST. Run 02_PORTABLE_OLUSTUR.bat from this clean package.
  if /I not "%~1"=="--auto" pause
  exit /b 1
)
findstr /C:"PASS:" "dist\Lithos_v1_0_2\GUI_EXE_TESTI.txt" >nul
if errorlevel 1 (
  echo EXE GUI TEST DID NOT PASS. Refusing to compile installer.
  if /I not "%~1"=="--auto" pause
  exit /b 1
)
set "ISCC="
where ISCC.exe >nul 2>nul
if not errorlevel 1 set "ISCC=ISCC.exe"
if not defined ISCC if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not defined ISCC if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not defined ISCC if exist "%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe" set "ISCC=%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"
if not defined ISCC if exist "%ProgramFiles(x86)%\Inno Setup 7\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 7\ISCC.exe"
if not defined ISCC if exist "%ProgramFiles%\Inno Setup 7\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 7\ISCC.exe"
if not defined ISCC (
  echo.
  echo Inno Setup 6 or 7 is required to make Setup.exe.
  echo Install it from https://jrsoftware.org/isdl.php
  echo Portable EXE is already available in dist\Lithos_v1_0_2.
  if /I not "%~1"=="--auto" pause
  exit /b 1
)
if not exist "assets\lithos_v102.ico" (
  echo Missing icon asset; installer cannot be compiled.
  if /I not "%~1"=="--auto" pause
  exit /b 1
)
if exist "dist\Lithos_v1.0.2_Setup.exe" del /Q "dist\Lithos_v1.0.2_Setup.exe"
"%ISCC%" "%CD%\installer.iss"
if errorlevel 1 goto :fail
if not exist "dist\Lithos_v1.0.2_Setup.exe" goto :fail
echo.
echo INSTALLER READY: %CD%\dist\Lithos_v1.0.2_Setup.exe
if /I not "%~1"=="--auto" pause
exit /b 0
:fail
echo.
echo SETUP FAILED. See Inno Setup error above.
if /I not "%~1"=="--auto" pause
exit /b 1
