@echo off
cd /d "%~dp0"
setlocal

set "VENV_PY=%~dp0.venv\Scripts\python.exe"
set "VENV_SITE=%~dp0.venv\Lib\site-packages"
set "UPX_DIR=%~dp0upx-5.1.1-win64"
set "ICO=%~dp0blur_ico.ico"
set "LOG=%~dp0build.log"

if not exist "%VENV_PY%" (
    echo [ERR] .venv\Scripts\python.exe not found
    pause
    exit /b 1
)
if not exist "%ICO%" (
    echo [ERR] blur_ico.ico not found
    pause
    exit /b 1
)

echo PyInstaller build start. Log -^> build.log
"%VENV_PY%" -m PyInstaller --noconfirm --windowed --clean --name "A-Blur" --icon "%ICO%" --paths "%VENV_SITE%" --upx-dir "%UPX_DIR%" --hidden-import keyboard --collect-submodules PySide6 --collect-submodules qfluentwidgets --add-data "blur_ico.ico;." --add-data "blur_ico.png;." blur.py > "%LOG%" 2>&1

set "RC=%errorlevel%"

echo PyInstaller done. Exit code %RC%
echo ----- last 50 lines of build.log -----
powershell -NoProfile -Command "Get-Content -Path '%LOG%' -Tail 50"
echo.
if "%RC%"=="0" (
    echo [OK] dist\A-Blur\A-Blur.exe
) else (
    echo [FAIL] code %RC%
)
echo Full log: %LOG%
pause
