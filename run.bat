@echo off
cd /d "%~dp0"
call .venv\Scripts\activate.bat
python blur.py
if errorlevel 1 pause
