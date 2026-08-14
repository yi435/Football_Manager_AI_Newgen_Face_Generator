@echo off
rem Deploys the website + the built EXE to Netlify.
rem The EXE is placed at site\download\FMNewgenGenerator.exe and served from
rem the Netlify site directly (works even while the GitHub repo is private).
rem Requires the Netlify CLI:  npm install -g netlify-cli  then  netlify login

setlocal
cd /d "%~dp0"

echo ===================================================
echo   Deploy site + EXE to Netlify
echo ===================================================

if not exist "netlify.toml" (
    echo [ERROR] netlify.toml not found in the project root.
    exit /b 1
)

if not exist "dist\FMNewgenGenerator.exe" (
    echo [ERROR] dist\FMNewgenGenerator.exe not found. Run build.bat first.
    exit /b 1
)

if not exist "site\download" mkdir "site\download"
copy /y "dist\FMNewgenGenerator.exe" "site\download\FMNewgenGenerator.exe" >nul
echo [Info] Copied EXE to site\download\FMNewgenGenerator.exe

echo [Info] Deploying the site/ folder with netlify.toml...
call netlify deploy --prod --dir=site

echo.
echo [Info] Done. The Download button points to /download/FMNewgenGenerator.exe
echo        on the deployed site. Keep the repo private if you like.
endlocal
pause