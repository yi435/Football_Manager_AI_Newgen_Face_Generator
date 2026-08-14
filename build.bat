@echo off
cd /d "%~dp0\.."
echo ===================================================
echo   Building FMNewgenGenerator.exe with PyInstaller
echo ===================================================
echo.
python -m pip install -r requirements.txt pyinstaller
if %errorlevel% neq 0 (
    echo [ERROR] Dependency install failed.
    pause
    exit /b 1
)
echo.
python -m PyInstaller --clean --noconfirm build\FMNewgenGenerator.spec
if %errorlevel% neq 0 (
    echo [ERROR] PyInstaller build failed.
    pause
    exit /b 1
)
echo.
echo [Success] Output: dist\FMNewgenGenerator.exe
pause