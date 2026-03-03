param(
    [Parameter(Mandatory = $false)]
    [ValidateSet("cloudflare", "localtunnel", "ngrok")]
    [string]$Provider = "cloudflare"
)

$WorkDir = Get-Location

# Ensure data directory exists
if (-not (Test-Path "$WorkDir\data")) { New-Item -ItemType Directory -Path "$WorkDir\data" -Force | Out-Null }

Write-Host "Starting Stable Tunnel ($Provider) for Onboarding Portal..." -ForegroundColor Green

switch ($Provider) {
    "cloudflare" {
        Write-Log "Initializing Cloudflare Tunnel..."
        # Ephemeral Cloudflare Quick Tunnel
        .\cloudflared.exe tunnel --url http://127.0.0.1:5010 --logfile data/tunnel.log
    }
    "localtunnel" {
        Write-Log "Initializing Localtunnel..."
        # Localtunnel check
        lt --port 5010 --subdomain "local-ai-onboarding-portal" > data/tunnel.log 2>&1
    }
    "ngrok" {
        Write-Log "Initializing Ngrok Tunnel..."
        # Ngrok (Requires auth token typically, assuming pre-configured)
        ngrok http 5010 --log=stdout > data/tunnel.log 2>&1
    }
}

function Write-Log($Msg) {
    $TS = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$TS] $Msg"
    "[$TS] $Msg" | Out-File -FilePath "$WorkDir\data\tunnel_startup.log" -Append
}
