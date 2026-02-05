# Robust Stable Tunnel Setup (Localtunnel)
# This script uses Localtunnel with a fixed subdomain for a persistent URL.

$WorkDir = Get-Location
$LogFile = "$WorkDir\data\tunnel.log"

Write-Host "Starting Stable Tunnel (Cloudflare) for Onboarding Portal..." -ForegroundColor Green
Write-Host "Requested URL: https://local-ai-onboarding-portal.trycloudflare.com" -ForegroundColor Yellow

# Run Cloudflare Tunnel (Password-Free)
# This will generate a random URL that is captured by monitor_services.ps1
# and pushed to GitHub Pages for a stable redirect.
.\cloudflared.exe tunnel --url http://127.0.0.1:5000 --logfile data/tunnel.log
