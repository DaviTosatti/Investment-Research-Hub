@echo off
setlocal DisableDelayedExpansion
set "HUB_POWERSHELL=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"
if exist "%SystemRoot%\Sysnative\WindowsPowerShell\v1.0\powershell.exe" set "HUB_POWERSHELL=%SystemRoot%\Sysnative\WindowsPowerShell\v1.0\powershell.exe"
"%HUB_POWERSHELL%" -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\windows\Start-Hub.ps1" -Action Stop %*
set "HUB_EXIT_CODE=%ERRORLEVEL%"
if not "%HUB_EXIT_CODE%"=="0" (
    echo.
    echo O Hub nao conseguiu parar. Codigo: %HUB_EXIT_CODE%.
    pause
)
exit /b %HUB_EXIT_CODE%
