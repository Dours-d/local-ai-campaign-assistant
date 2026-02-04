
# Seamless Tunnel Setup (Cloudflare)
# This script ensures cloudflared is available and runs it to provide a password-free link.

$WorkDir = Get-Location
$ExePath = "$WorkDir\cloudflared.exe"

if (-not (Test-Path $ExePath)) {
    Write-Host "Cloudflared not found. Downloading portable version..." -ForegroundColor Cyan
    $Url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
    Invoke-WebRequest -Uri $Url -OutFile $ExePath
}

Write-Host "`nStarting Seamless Tunnel for Onboarding Portal..." -ForegroundColor Green
Write-Host "The link below starting with https://... will be PASSWORD-FREE for users.`n" -ForegroundColor Yellow

# Run cloudflared tunnel
& $ExePath tunnel --url http://localhost:5000
