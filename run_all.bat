@echo off
cd /d "%~dp0"
title FM AI Newgen Generator + ComfyUI Launcher
echo ===================================================
echo   FM AI Newgen Generator + ComfyUI Launcher
echo ===================================================
echo.

:: 1. Launch ComfyUI in a new window
echo Starting ComfyUI server in the background...
if exist "%LOCALAPPDATA%\FM Newgen Generator\ComfyUI_windows_portable\run_nvidia_gpu.bat" (
    start "ComfyUI Server" /min cmd /c "%LOCALAPPDATA%\FM Newgen Generator\ComfyUI_windows_portable\run_nvidia_gpu.bat"
    echo [Success] Embedded ComfyUI launch triggered. Waiting 5 seconds for server boot...
    timeout /t 5 >nul
) else if exist "%USERPROFILE%\ComfyUI\run_nvidia_gpu.bat" (
    start "ComfyUI Server" /min cmd /c "%USERPROFILE%\ComfyUI\run_nvidia_gpu.bat"
    echo [Success] ComfyUI launch triggered. Waiting 5 seconds for server boot...
    timeout /t 5 >nul
) else (
    echo [Info] ComfyUI will be auto-started by the application if installed, or start it manually.
    echo.
)

:: 2. Check Python installation
echo Checking Python environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your system PATH!
    echo Please download and install Python 3.10+ from python.org
    echo and tick the box "[x] Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

:: 3. Install/update dependencies
echo Installing/updating Python dependencies...
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [WARNING] Dependency sync failed. Trying to start application anyway...
)

:: 4. Run the application
echo.
echo Starting FM AI Newgen Generator App...
python -m src.app
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Application closed with an error.
    pause
)
