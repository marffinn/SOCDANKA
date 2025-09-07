@echo off
setlocal

echo.
echo WARNING: Your system PATH is in a fragile state. This script will
echo attempt a low-level repair using PowerShell. This is a last resort.
echo If this fails, you MUST fix the PATH manually via the GUI.
echo.
echo IMPORTANT: This script MUST be run as an administrator.
echo.
pause

:: Check for admin rights and self-elevate
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

set "POWERSHELL_EXE=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"

if not exist "%POWERSHELL_EXE%" (
    echo CRITICAL ERROR: PowerShell executable not found at %POWERSHELL_EXE%
    echo Cannot proceed. Your Windows installation is likely corrupted.
    pause
    exit /B
)

echo Found PowerShell. Attempting to repair PATH...

"%POWERSHELL_EXE%" -NoProfile -ExecutionPolicy Bypass -Command "
    try {
        $keyPath = 'SYSTEM\CurrentControlSet\Control\Session Manager\Environment';
        $regPath = "Registry::HKEY_LOCAL_MACHINE\$keyPath";
        $oldPath = (Get-ItemProperty -Path $regPath -Name Path -ErrorAction Stop).Path;
        $pathEntries = $oldPath -split ';' | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne '' };

        $pathsToAdd = @(
            [System.Environment]::ExpandEnvironmentVariables('%SystemRoot%\System32'),
            [System.Environment]::ExpandEnvironmentVariables('%SystemRoot%'),
            [System.Environment]::ExpandEnvironmentVariables('%SystemRoot%\System32\Wbem'),
            [System.Environment]::ExpandEnvironmentVariables('%SystemRoot%\System32\WindowsPowerShell\v1.0'),
            'C:\Program Files\Git\cmd',
            'C:\Program Files\Git\bin'
        );

        Write-Host 'Checking and adding required paths...';
        $pathList = [System.Collections.Generic.List[string]]@($pathEntries);

        foreach ($p in $pathsToAdd) {
            if ($pathList -notcontains $p) {
                Write-Host "  - Adding: $p";
                $pathList.Add($p);
            } else {
                Write-Host "  - Already present: $p";
            }
        }

        $newPathString = $pathList -join ';';
        Set-ItemProperty -Path $regPath -Name Path -Value $newPathString -ErrorAction Stop;

        Write-Host 'Successfully updated system PATH.';
    } catch {
        Write-Host "An error occurred: $_" -ForegroundColor Red;
        exit 1;
    }
"

if %errorlevel% == 0 (
    echo.
    echo --- RESTART REQUIRED ---
    echo To apply these critical changes, you must restart your computer.
    echo Please save all your work and restart now.
) else (
    echo.
    echo ERROR: The PowerShell script failed to update the system PATH.
    echo It is highly recommended to fix the PATH manually through the GUI as previously instructed.
)


echo.
pause
