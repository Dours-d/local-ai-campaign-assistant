@echo off
cd /d "%~dp0"
echo Starting Applet Debugger...
echo.
echo Python Path:
where python
echo.
echo Running Script...
"C:\Users\gaelf\AppData\Local\Programs\Python\Python313\python.exe" scripts\onboarding_shortcut.py
pause
