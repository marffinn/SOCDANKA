@echo off
setlocal

echo [INFO] Starting automated build and release process...

REM Load GitHub token from .env file (using working pattern)
for /f "tokens=1* delims==" %%a in ('type .env ^| findstr /b "GITHUB_TOKEN="') do (
    set "GH_TOKEN=%%b"
)

if not defined GH_TOKEN (
    echo [ERROR] GITHUB_TOKEN not found in .env file
    pause
    exit /b 1
)

REM Generate version using random number
set /a "rand=%RANDOM%"
set "VERSION=v1.0.%rand%"

echo [INFO] Building version: %VERSION%

REM Clean previous builds
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build

REM Install dependencies
echo [INFO] Installing dependencies...
pip install -r requirements.txt >nul 2>&1
pip install pyinstaller >nul 2>&1

REM Build executable
echo [INFO] Building executable...
pyinstaller SOCDunk.spec
if not exist "dist\SOCDunk.exe" (
    echo [ERROR] Build failed - executable not found
    pause
    exit /b 1
)

REM Set up GitHub repository URL with token
set "GITHUB_USERNAME=marffinn"
set "REPO_NAME=SOCDBitchBetterRecognize"

set "REPO_URL=https://%GITHUB_USERNAME%:%GH_TOKEN%@github.com/marffinn/SOCDANKA.git"

REM Check if tag exists and delete if necessary
echo [INFO] Checking for existing tag %VERSION%...
git tag -l %VERSION% >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] Deleting existing local tag %VERSION%...
    git tag -d %VERSION%
)

git ls-remote --tags origin %VERSION% | findstr /C:"refs/tags/%VERSION%" >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] Deleting existing remote tag %VERSION%...
    git push %REPO_URL% :refs/tags/%VERSION%
)

REM Create and push new tag
echo [INFO] Creating tag %VERSION%...
git tag %VERSION%
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create tag
    pause
    exit /b 1
)

echo [INFO] Pushing tag to GitHub...
git push %REPO_URL% %VERSION%
if %errorlevel% neq 0 (
    echo [ERROR] Failed to push tag
    pause
    exit /b 1
)

echo [SUCCESS] Release %VERSION% created successfully!
echo [INFO] GitHub Actions should trigger automatically to create the release
echo [INFO] Check: https://github.com/marffinn/SOCDANKA/releases
pause