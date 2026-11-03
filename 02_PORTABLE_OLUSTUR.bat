@echo off
setlocal EnableExtensions
cd /d "%~dp0"
echo.
echo [Lithos v1.0.2] Clean build with MANDATORY GUI startup verification
rem FAIL FAST: packaging must contain every required file before creating venv.
if not exist "%~dp0requirements.txt" goto :missing_inputs
if not exist "%~dp0KULLANIM_TR_EN.txt" goto :missing_inputs
if not exist "%~dp0VERSIYON_NOTLARI.txt" goto :missing_inputs
if not exist "%~dp0ACCESS_SABLON_OLUSTUR.ps1" goto :missing_inputs
if not exist "%~dp0installer.iss" goto :missing_inputs
if not exist "%~dp0lithos\app.py" goto :missing_inputs
if not exist "%~dp0assets\lithos_v102.ico" goto :missing_inputs
if not exist "%~dp0veri_sozlugu\GURBELEN18_lookup_TR_EN.csv" goto :missing_inputs
echo [OK] Required project files are present.
set "PYVER="
for %%V in (3.12 3.13 3.14) do (
  if not defined PYVER (
    py -%%V -c "import sys" >nul 2>nul
    if not errorlevel 1 set "PYVER=%%V"
  )
)
if defined PYVER goto :have_python
echo Python 3.12/3.13/3.14 not found. Keep Python 3.15 installed.
echo Install an additional Python 3.12: winget install -e --id Python.Python.3.12
if /I not "%~1"=="--auto" pause
exit /b 1
:have_python
echo Python %PYVER%
set "VENV=.build_lithos_%PYVER%"
if not exist "%VENV%\Scripts\python.exe" (
  py -%PYVER% -m venv "%VENV%"
  if errorlevel 1 goto :fail
)
rem Keep existing pip. Avoid unnecessary upgrade and network traffic.
"%VENV%\Scripts\python.exe" -m pip install --only-binary=:all: -r "%~dp0requirements.txt"
if errorlevel 1 goto :fail
"%VENV%\Scripts\python.exe" -m pip install --only-binary=:all: "pyinstaller>=6,<7"
if errorlevel 1 goto :fail

echo.
echo [0/4] Verify BOTH prebuilt original-schema Access templates.
if not exist "Templates\Lithos_GURBELEN18_Bos.accdb" goto :prepare_templates
if not exist "Templates\Lithos_GURBELEN18_Bos_EN.accdb" goto :prepare_templates
goto :templates_ready
:prepare_templates
echo No premade templates found. Generate them ONCE, during this Windows build.
echo Lithos will never ask users to generate templates when the app opens.
call "01_ACCESS_SABLONLARI_OLUSTUR.bat" --auto
if errorlevel 1 goto :fail
:templates_ready
if not exist "Templates\Lithos_GURBELEN18_Bos.accdb" goto :fail
if not exist "Templates\Lithos_GURBELEN18_Bos_EN.accdb" goto :fail
echo [1/4] Compile ALL Python files, refuse broken imports
"%VENV%\Scripts\python.exe" -m compileall -q -f lithos gui.py
if errorlevel 1 goto :fail

echo [2/4] Run report + schema regression tests
"%VENV%\Scripts\python.exe" -m unittest discover -s tests -v
if errorlevel 1 goto :fail

echo [3/4] ACTUALLY import and construct Qt GUI in offscreen mode
"%VENV%\Scripts\python.exe" -m lithos.preflight --output "GUI_KAYNAK_TESTI.txt"
if errorlevel 1 goto :fail
findstr /C:"PASS:" "GUI_KAYNAK_TESTI.txt" >nul
if errorlevel 1 goto :fail

echo [4/4] Build frozen application and smoke-test its import/GUI
if exist "dist\Lithos_v1_0_2" rmdir /S /Q "dist\Lithos_v1_0_2"
"%VENV%\Scripts\python.exe" -m PyInstaller --noconfirm --clean --onedir --windowed --name Lithos_v1_0_2 --icon "assets\lithos_v102.ico" --add-data "assets;assets" --add-data "veri_sozlugu;veri_sozlugu" --hidden-import pyodbc --collect-all PySide6 --collect-all matplotlib gui.py
if errorlevel 1 goto :fail
if not exist "dist\Lithos_v1_0_2\Lithos_v1_0_2.exe" goto :fail
if not exist "dist\Lithos_v1_0_2\Templates" mkdir "dist\Lithos_v1_0_2\Templates"
for %%F in ("Templates\Lithos_GURBELEN18_Bos.accdb" "Templates\Lithos_GURBELEN18_Bos_EN.accdb") do if exist "%%~fF" copy /Y "%%~fF" "dist\Lithos_v1_0_2\Templates" >nul
copy /Y "KULLANIM_TR_EN.txt" "dist\Lithos_v1_0_2\KULLANIM_TR_EN.txt" >nul
if errorlevel 1 goto :fail
copy /Y "VERSIYON_NOTLARI.txt" "dist\Lithos_v1_0_2\VERSIYON_NOTLARI.txt" >nul
if errorlevel 1 goto :fail
if exist "dist\Lithos_v1_0_2\GUI_EXE_TESTI.txt" del /Q "dist\Lithos_v1_0_2\GUI_EXE_TESTI.txt"
start "" /wait "dist\Lithos_v1_0_2\Lithos_v1_0_2.exe" --self-test "%CD%\dist\Lithos_v1_0_2\GUI_EXE_TESTI.txt"
if errorlevel 1 goto :fail
if not exist "dist\Lithos_v1_0_2\GUI_EXE_TESTI.txt" goto :fail
findstr /C:"PASS:" "dist\Lithos_v1_0_2\GUI_EXE_TESTI.txt" >nul
if errorlevel 1 goto :fail
echo.
echo SUCCESS: Portable was built AND its Qt startup passed.
echo Use WHOLE dist\Lithos_v1_0_2 folder; do not move EXE alone.
if /I not "%~1"=="--auto" pause
exit /b 0
:missing_inputs
echo.
echo ERROR: This project folder is incomplete.
echo Required: requirements.txt, KULLANIM_TR_EN.txt, VERSIYON_NOTLARI.txt,
echo ACCESS_SABLON_OLUSTUR.ps1, installer.iss, lithos, assets and veri_sozlugu.
echo Do not mix this folder with previous Lithos versions.
if /I not "%~1"=="--auto" pause
exit /b 1
:fail
echo.
echo BUILD STOPPED: Do NOT install an untested application.
echo See GUI_KAYNAK_TESTI.txt or dist\Lithos_v1_0_2\GUI_EXE_TESTI.txt if available.
if /I not "%~1"=="--auto" pause
exit /b 1
