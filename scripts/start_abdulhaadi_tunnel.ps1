# Start Persistent Tunnel for Abdulhaadi
# Uses Localtunnel to request a fixed subdomain "abdulhaadi"

$Subdomain = "abdulhaadi"
$Port = 5000

Write-Host "Starting Access Portal at https://$Subdomain.loca.lt" -ForegroundColor Green

# Use npx to avoid path issues, or direct lt command if in path
# We use --print-requests to keep the process alive and visible
lt --port $Port --subdomain $Subdomain
