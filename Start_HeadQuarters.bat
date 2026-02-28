@echo off
TITLE Sovereign HeadQuarters Boot
echo Starting Sovereign HeadQuarters...
echo.

:: We rely on the watchdog (monitor_services.ps1) to keep the backend API alive on port 5010.
start /MIN powershell -ExecutionPolicy Bypass -File "scripts\monitor_services.ps1"

:: Wait a brief moment to ensure startup
timeout /t 5 /nobreak >nul

:: Open a new Google Chrome instance with all necessary workspaces
start chrome --new-window "http://127.0.0.1:5010/mgmt" "https://whydonate.com/register/login"

echo Campaign Management Corridor launched. You can close this window.
timeout /t 2 >nul
exit
