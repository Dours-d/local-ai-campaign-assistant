param(
    [string]$Provider = "cloudflare"
)

$WorkDir = Get-Location
$LogFile = "$WorkDir\data\tunnel.log"

Remove-Item -Path $LogFile -ErrorAction SilentlyContinue

Write-Host "Starting Stable Tunnel for Onboarding Portal using $Provider..." -ForegroundColor Green

if ($Provider -eq "cloudflare") {
    .\cloudflared.exe tunnel --url http://127.0.0.1:5010 --logfile $LogFile
}
elseif ($Provider -eq "localtunnel") {
    npx localtunnel --port 5010 --subdomain local-ai-onboarding-portal > $LogFile
}
elseif ($Provider -eq "ngrok") {
    ngrok http 5010 --log $LogFile
}
