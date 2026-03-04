# Sovereign Node: Persistent Named Tunnel Setup
# Guides the user through creating a non-rotating Cloudflare tunnel.

$WorkDir = "c:\Users\gaelf\Documents\GitHub\local_ai_campaign_assistant"
$CloudflaredPath = "$WorkDir\cloudflared.exe"
$ConfigPath = "$WorkDir\.cloudflared\config.yml"

Write-Host "`n" + "="*60 -ForegroundColor Cyan
Write-Host "  [ SOVEREIGN INFRASTRUCTURE: NAMED TUNNEL SETUP ]" -ForegroundColor Cyan
Write-Host "="*60 + "`n" -ForegroundColor Cyan

if (-not (Test-Path $CloudflaredPath)) {
    Write-Host "[!] Error: cloudflared.exe not found in $WorkDir" -ForegroundColor Red
    exit 1
}

Write-Host "This script will help you transition from random ephemeral URLs to " -ForegroundColor Gray
Write-Host "a persistent Sovereign URL (e.g. brain.fajr.today).`n" -ForegroundColor Gray

# 1. Login
Write-Host "Step 1: Authenticate with Cloudflare" -ForegroundColor Yellow
Write-Host "A browser window will open. Login and authorize the 'fajr.today' domain if applicable.`n" -ForegroundColor Gray
& $CloudflaredPath tunnel login

# 2. Create Tunnel
Write-Host "`nStep 2: Create the Tunnel" -ForegroundColor Yellow
$TunnelName = "sovereign-node"
Write-Host "Creating tunnel named '$TunnelName'..." -ForegroundColor Gray
$TunnelOutput = & $CloudflaredPath tunnel create $TunnelName
Write-Host $TunnelOutput

# Extract Tunnel ID
$TunnelId = if ($TunnelOutput -match "Created tunnel \w+ with id ([a-f0-9-]+)") { $Matches[1] } else { 
    Write-Host "[!] Could not extract Tunnel ID from output. Please enter it manually if you see it above:" -ForegroundColor Magenta
    Read-Host "Tunnel ID"
}

if (-not $TunnelId) { Write-Host "[!] Canceled." -ForegroundColor Red; exit 1 }

# 3. Generate Config
Write-Host "`nStep 3: Generating Config" -ForegroundColor Yellow
$ConfigDir = Split-Path $ConfigPath
if (-not (Test-Path $ConfigDir)) { New-Item -ItemType Directory -Path $ConfigDir }

$ConfigContent = @"
tunnel: $TunnelId
credentials-file: C:\Users\gaelf\.cloudflared\$TunnelId.json

ingress:
  - hostname: brain.fajr.today
    service: http://localhost:5010
  - service: http_status:404
"@

$ConfigContent | Out-File -FilePath $ConfigPath -Encoding utf8
Write-Host "Config saved to $ConfigPath" -ForegroundColor Green

# 4. Final Instructions
Write-Host "`n" + "="*60 -ForegroundColor Cyan
Write-Host "  [ SETUP COMPLETE ]" -ForegroundColor Green
Write-Host "="*60 -ForegroundColor Cyan
Write-Host "To finalize the routing, you must add a CNAME record in your Cloudflare DNS:" -ForegroundColor Gray
Write-Host "  Type: CNAME" -ForegroundColor White
Write-Host "  Name: brain" -ForegroundColor White
Write-Host "  Target: $TunnelId.cfargotunnel.com" -ForegroundColor White
Write-Host "  Proxy: Enabled (Orange Cloud)`n" -ForegroundColor White

Write-Host "Once DNA is set, 'monitor_services.ps1' will use this persistent link." -ForegroundColor Gray
Write-Host "="*60 -ForegroundColor Cyan
