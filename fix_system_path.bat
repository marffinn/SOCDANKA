@echo off
setlocal

echo This script will restore essential Windows system directories (like System32
echo and PowerShell) to the system PATH. This should fix errors where common
echo commands like 'powershell.exe' are not recognized.

echo.
echo IMPORTANT: This script MUST be run as an administrator.
echo.
pause


:: Check for admin rights and self-elevate if necessary
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


echo Reading the current system PATH from the registry...

for /f "tokens=2,*" %%a in ('reg query "HKLM\System\CurrentControlSet\Control\Session Manager\Environment" /v Path') do (
    set "SYSTEM_PATH=%%b"
)


:: Define essential paths to check and add
set "ESSENTIAL_PATHS=%SystemRoot%\System32;%SystemRoot%;%SystemRoot%\System32\Wbem;%SystemRoot%\System32\WindowsPowerShell\v1.0"

echo.
echo The following essential paths will be appended to the system PATH if missing:
echo   - %SystemRoot%\System32
echo   - %SystemRoot%
echo   - %SystemRoot%\System32\Wbem
echo   - %SystemRoot%\System32\WindowsPowerShell\v1.0
echo.


:: Append the paths to the current system PATH
:: Using setx /M to modify the machine-level PATH variable
setx /M PATH "%SYSTEM_PATH%;%ESSENTIAL_PATHS%"

if %errorlevel% == 0 (
    echo Successfully updated the system PATH.
) else (
    echo ERROR: Failed to update the system PATH.
)

echo.
echo --- RESTART REQUIRED ---
echo To apply these critical changes, you must restart your computer.
echo Please save all your work and restart now.
echo.
pause
