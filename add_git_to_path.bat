@echo off
setlocal

:: --- Configuration ---
:: IMPORTANT: Change this path to your actual Git installation directory.
set "GIT_INSTALL_PATH=C:\Program Files\Git"
:: -------------------

set "GIT_CMD_PATH=%GIT_INSTALL_PATH%\cmd"
set "GIT_BIN_PATH=%GIT_INSTALL_PATH%\bin"

echo This script will add the following directories to the system PATH:
echo   - %GIT_CMD_PATH%
echo   - %GIT_BIN_PATH%
echo.
echo IMPORTANT: This script must be run as an administrator.
echo.
pause

>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if '%errorlevel%' NEQ '0' (
    echo Requesting administrative privileges...
    goto UACPrompt
) else (
    goto gotAdmin
)

:UACPrompt
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\getadmin.vbs"
    "%temp%\getadmin.vbs"
    exit /B

:gotAdmin
    if exist "%temp%\getadmin.vbs" ( del "%temp%\getadmin.vbs" )
    pushd "%CD%"
    CD /D "%~dp0"

echo Checking for existing Git paths...

for /f "tokens=2,*" %%a in ('reg query "HKLM\System\CurrentControlSet\Control\Session Manager\Environment" /v Path') do (
    set "SYSTEM_PATH=%%b"
)

set "NEEDS_CMD_PATH=true"
echo "%SYSTEM_PATH%" | find /I "%GIT_CMD_PATH%" > nul
if %errorlevel% == 0 (
    echo   - %GIT_CMD_PATH% is already in the system PATH.
    set "NEEDS_CMD_PATH=false"
)

set "NEEDS_BIN_PATH=true"
echo "%SYSTEM_PATH%" | find /I "%GIT_BIN_PATH%" > nul
if %errorlevel% == 0 (
    echo   - %GIT_BIN_PATH% is already in the system PATH.
    set "NEEDS_BIN_PATH=false"
)

if "%NEEDS_CMD_PATH%"=="false" if "%NEEDS_BIN_PATH%"=="false" (
    echo.
    echo No changes needed.
    goto end
)

set "NEW_PATH=%SYSTEM_PATH%"
if "%NEEDS_CMD_PATH%"=="true" (
    echo Appending %GIT_CMD_PATH%...
    set "NEW_PATH=%NEW_PATH%;%GIT_CMD_PATH%"
)
if "%NEEDS_BIN_PATH%"=="true" (
    echo Appending %GIT_BIN_PATH%...
    set "NEW_PATH=%NEW_PATH%;%GIT_BIN_PATH%"
)

echo.
echo Updating system PATH...
setx /M PATH "%NEW_PATH%"

if %errorlevel% == 0 (
    echo.
    echo Successfully updated the system PATH.
) else (
    echo.
    echo ERROR: Failed to update the system PATH.
)

:end
echo.
echo Please restart your GitHub Actions runner and any open terminals for the changes to take effect.
pause
