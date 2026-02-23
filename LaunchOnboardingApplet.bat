@echo off
pushd "%~dp0"
echo Launching Amanah Onboarding Applet...
python scripts/onboarding_applet.py
popd
pause
