@echo off
setlocal

:: Check for arguments
if "%~1"=="" (
    goto :push_to_main_only
)

set "VERSION_TAG=%~1"
if not "%VERSION_TAG:~0,1%"=="v" (
    set "VERSION_TAG=v%VERSION_TAG%"
)

set "GITHUB_USERNAME=marffinn"

:: Load environment variables from .env file
for /f "tokens=1* delims==" %%a in ('type .env ^| findstr /b "GH_TOKEN="') do (
    set "%%a=%%b"
)

if not defined GH_TOKEN (
    echo Error: GH_TOKEN not found in .env file.
    exit /b 1
)

set "REPO_URL=https://%GITHUB_USERNAME%:%GH_TOKEN%@github.com/marffinn/u-qw-sb.git"

echo.
echo --- Building and Releasing %VERSION_TAG% ---
echo.

:: 1. Build executable
echo Running pyinstaller...
pyinstaller BROWSANKA.spec
if %errorlevel% neq 0 (
    echo Error: pyinstaller failed.
    exit /b 1
)

:: 2. Prepare executable_dist
echo Preparing executable_dist directory...
call prepare_executable_dist.bat
if %errorlevel% neq 0 (
    echo Error: prepare_executable_dist.bat failed.
    exit /b 1
)

:: 3. Build the installer
echo Building NSIS installer...
makensis installers\windows\installer.nsi
if %errorlevel% neq 0 (
    echo Error: makensis failed.
    exit /b 1
)

:: Extract version number from VERSION_TAG (e.g., v1.0.0 -> 1.0.0)
set "APP_VERSION=%VERSION_TAG:~1%"

:: 4. Create release directory
if not exist "release" (
    mkdir "release"
    if %errorlevel% neq 0 (
        echo Error: Failed to create release directory.
        exit /b 1
    )
)

:: Clean release directory
echo Cleaning release directory...
del /Q "release\*"
if %errorlevel% neq 0 (
    echo Warning: Failed to clean release directory. Continuing anyway.
)

:: 5. Move the installer
echo Moving installer to release directory...
move "installers\windows\BROWSANKA-Setup-1.0.0.exe" "release\BROWSANKA-Setup-%APP_VERSION%.exe"
if %errorlevel% neq 0 (
    echo Error: Failed to move installer.
    exit /b 1
)

:: 6. Commit the installer
echo Committing installer to git...
git add "release\BROWSANKA-Setup-%APP_VERSION%.exe"
if %errorlevel% neq 0 (
    echo Error: Failed to add installer to git.
    exit /b 1
)
git commit -m "feat(release): add BROWSANKA-Setup-%APP_VERSION%.exe"
if %errorlevel% neq 0 (
    echo Error: Failed to commit installer.
    exit /b 1
)

:: 7. Push the commit
echo Pushing commit to main branch...
git push %REPO_URL% main
if %errorlevel% neq 0 (
    echo Error: Failed to push commit to main.
    exit /b 1
)

:: 8. Tagging logic (existing)
echo.
echo --- Processing tag: %VERSION_TAG% ---
echo.

:: Check if tag exists locally
git tag -l %VERSION_TAG% >nul 2>&1
if %errorlevel% equ 0 (
    echo Local tag "%VERSION_TAG%" found. Deleting local tag...
    git tag -d %VERSION_TAG%
    if %errorlevel% neq 0 (
        echo Error deleting local tag. Exiting.
        exit /b 1
    )
)

:: Check if tag exists on remote
echo Checking if remote tag "%VERSION_TAG%" exists...
git ls-remote --tags origin %VERSION_TAG% | findstr /C:"refs/tags/%VERSION_TAG%" >nul 2>&1
if %errorlevel% equ 0 (
    echo Remote tag "%VERSION_TAG%" found. Deleting remote tag...
    git push %REPO_URL% :refs/tags/%VERSION_TAG%
    if %errorlevel% neq 0 (
        echo Error deleting remote tag. Exiting.
        exit /b 1
    )
)

echo Creating new local tag "%VERSION_TAG%"...
git tag %VERSION_TAG%
if %errorlevel% neq 0 (
    echo Error creating local tag. Exiting.
    exit /b 1
)

echo Pushing tag "%VERSION_TAG%" to GitHub...
git push %REPO_URL% %VERSION_TAG%
if %errorlevel% neq 0 (
    echo Error pushing tag to GitHub. Exiting.
    exit /b 1
)

echo.
echo Release process for %VERSION_TAG% completed successfully.
echo GitHub Actions workflow should be triggered.
echo.

endlocal
exit /b 0

:push_to_main_only
echo.
echo --- Pushing to main branch only ---
echo.
set "GITHUB_USERNAME=marffinn"
:: Load environment variables from .env file
for /f "tokens=1* delims==" %%a in ('type .env ^| findstr /b "GH_TOKEN="') do (
    set "%%a=%%b"
)
if not defined GH_TOKEN (
    echo Error: GH_TOKEN not found in .env file.
    exit /b 1
)
set "REPO_URL=https://%GITHUB_USERNAME%:%GH_TOKEN%@github.com/marffinn/u-qw-sb.git"
echo Pushing commit to main branch...
git push %REPO_URL% main
if %errorlevel% neq 0 (
    echo Error: Failed to push commit to main.
    exit /b 1
)
echo Push to main completed successfully.
exit /b 0