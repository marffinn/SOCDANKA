@echo off
setlocal

echo This script will add your Python installation directory and its Scripts
echo subdirectory to your user PATH variable, allowing you to run 'python'
rem and other tools like 'pip' and 'pyinstaller' from any terminal.

echo.
echo --- Step 1: Find your Python Installation Folder ---
echo Before you continue, you need to know where Python is installed.
echo Common locations are:
echo   - C:\Python311
echo   - C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311
echo (The version number might be different on your system).
echo.
pause

:getPath
set "PYTHON_PATH="
echo.
echo --- Step 2: Enter the Python Path ---
set /p "PYTHON_PATH=Please enter the full path to your Python installation folder: "

if not defined PYTHON_PATH (
    echo.
    echo You did not enter a path. Please try again.
    goto getPath
)

if not exist "%PYTHON_PATH%\python.exe" (
    echo.
    echo ERROR: I couldn't find python.exe in that folder.
    echo Please make sure the path is correct and try again.
    goto getPath
)

set "SCRIPTS_PATH=%PYTHON_PATH%\Scripts"

echo.
echo --- Step 3: Confirmation ---
echo The following directories will be added to your user PATH:
echo   - %PYTHON_PATH%
if exist "%SCRIPTS_PATH%" (
    echo   - %SCRIPTS_PATH%
) else (
    echo (Warning: Scripts directory not found, will only add the main directory)
)
echo.
pause


echo.
echo --- Step 4: Updating PATH ---

rem We need to get the current user path and append to it.
rem setx does not expand variables from the current session, so we read from registry.
for /f "tokens=2,*" %%a in ('reg query HKCU\Environment /v Path') do (
    set "USER_PATH=%%b"
)

set "NEW_PATH=%USER_PATH%"

echo "%USER_PATH%" | find /I "%PYTHON_PATH%" > nul
if %errorlevel% == 0 (
    echo   - %PYTHON_PATH% is already in your PATH.
) else (
    echo   - Adding %PYTHON_PATH%...
    set "NEW_PATH=%NEW_PATH%;%PYTHON_PATH%"
)

if exist "%SCRIPTS_PATH%" (
    echo "%USER_PATH%" | find /I "%SCRIPTS_PATH%" > nul
    if %errorlevel% == 0 (
        echo   - %SCRIPTS_PATH% is already in your PATH.
    ) else (
        echo   - Adding %SCRIPTS_PATH%...
        set "NEW_PATH=%NEW_PATH%;%SCRIPTS_PATH%"
    )
)

setx PATH "%NEW_PATH%"

echo.
echo --- Complete! ---
echo Successfully updated your user PATH.
echo IMPORTANT: You must CLOSE and REOPEN your PowerShell or terminal window
echo for the changes to take effect.
echo.
pause
