@echo off
setlocal EnableExtensions
cd /d "%~dp0"
echo.
echo ==============================================================
echo  LITHOS v1.0.2 - ORIGINAL GURBELEN ACCESS AND DESKTOP APP
 echo ==============================================================
echo.
echo On this WINDOWS computer, both empty ACCDB templates are generated
 echo during the package build, NOT at Lithos program startup.
echo Place original GURBELEN-18.accdb NEXT to this BAT, if possible.
echo It will be read ONLY; its research records are never bundled.
echo.
call "02_PORTABLE_OLUSTUR.bat" --auto
if errorlevel 1 goto :failed
echo.
echo Portable program and both empty Access templates are ready.
choice /C YN /M "Create Windows Setup.exe using Inno Setup too?"
if errorlevel 2 goto :done
call "03_KURULUM_OLUSTUR.bat" --auto
if errorlevel 1 goto :failed
:done
echo.
echo DONE. Lithos has NO first-launch database creation wizard.
pause
exit /b 0
:failed
echo.
echo BUILD STOPPED. Do not install an incomplete release.
pause
exit /b 1
