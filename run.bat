@echo off
title FM AI Newgen Generator Launcher
echo ===================================================
echo   Football Manager AI Newgen Generator Launcher
echo ===================================================
echo.

:: Check Python installation
echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your system PATH!
    echo.
    echo Please download and install Python 3.10 or newer from:
    echo https://www.python.org/downloads/
    echo.
    echo CRITICAL: During installation, make sure to check the box:
    echo "[x] Add Python.exe to PATH"
    echo.
    pause
    exit /b 1
)

:: Install/update dependencies
echo.
echo Installing/updating Python dependencies...
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo [WARNING] Dependency installation failed! The application might still run 
    echo if the packages are already installed.
    echo.
)

:: Run the application
echo.
echo Starting FM AI Newgen Generator...
python src/app.py
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Application crashed or stopped with an error code.
    echo.
    pause
)
