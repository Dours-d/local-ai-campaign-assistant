@echo off
echo Closing all Chrome instances...
taskkill /F /IM chrome.exe /T >nul 2>&1
echo Starting Chrome in Debug Mode...
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\ChromeDevSession" --remote-allow-origins=*
echo Done! You can now log in to the required platforms.
pause
