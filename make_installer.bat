@echo off
cd /d "%~dp0"
setlocal

set "NSIS=%~dp0nsis-3.09\makensis.exe"

if not exist "%NSIS%" (
    echo [ERR] makensis.exe not found at: %NSIS%
    pause
    exit /b 1
)

set "BASE=%~dp0"
if "%BASE:~-1%"=="\" set "BASE=%BASE:~0,-1%"

echo NSIS build start.
"%NSIS%" -DBUILD_SRC="%BASE%\dist\A-Blur" -DOUT_DIR="%BASE%" "installer.nsi"

set "RC=%errorlevel%"
echo NSIS done. Exit code %RC%
if "%RC%"=="0" (
    echo [OK] A-Blur-Setup.exe
) else (
    echo [FAIL] code %RC%
)
pause
