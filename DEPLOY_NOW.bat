@echo off
echo 🚀 Initiating Comprehensive Deployment for fajr.today...

:: 1. Deploy Landing Page (frontend folder)
echo 📡 Deploying Landing Page...
npx wrangler pages deploy frontend --project-name=fajr-today-landing
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Landing Page Deployment Failed.
) else (
    echo ✅ Landing Page Deployed!
)

:: 2. Generate and Deploy Campaigns (vault/amplification)
echo 📡 Generating Campaigns Index...
python scripts/generate_fajr_directory.py
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Campaigns Generation Failed.
) else (
    echo 📡 Deploying Campaigns Directory...
    npx wrangler pages deploy vault/amplification --project-name=fajr-today
    if %ERRORLEVEL% NEQ 0 (
        echo ❌ Campaigns Deployment Failed.
    ) else (
        echo ✅ Campaigns Deployed!
    )
)

echo.
echo 🎉 Deployment Process Complete.
pause
