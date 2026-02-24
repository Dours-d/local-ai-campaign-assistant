# Robust Monitor for Onboarding Server and Cloudflare Tunnel
# This script ensures both the intake server and the tunnel stay running all day.

$LogFile = "data/monitoring.log"
$WorkDir = Get-Location
$ServerScript = "scripts/onboarding_server.py"
$VenvPython = "$WorkDir\.venv\Scripts\python.exe"

function Write-Log($Message) {
    if ($null -eq $Message) { return }
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "[$Timestamp] $Message"
    Write-Host $LogEntry -ForegroundColor Cyan
    if (-not (Test-Path "data")) { New-Item -ItemType Directory -Path "data" -Force }
    $LogEntry | Out-File -FilePath $LogFile -Append
}

$ConnectivityRetries = 0
$MaxRetries = 3

while ($true) {
    # 1. Check Onboarding Server Process
    $ServerProcess = Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*onboarding_server.py*" }
    if (-not $ServerProcess) {
        Write-Log "Onboarding Server NOT found. Restarting..."
        Start-Process $VenvPython -ArgumentList "$ServerScript" -WorkingDirectory $WorkDir -WindowStyle Hidden
        Start-Sleep -Seconds 5
    }

    # 2. Check Local Health (Precision Check)
    try {
        $LocalHealth = Invoke-WebRequest -Uri "http://127.0.0.1:5010/health" -Method Get -TimeoutSec 5 -ErrorAction Stop
    }
    catch {
        Write-Log "Local Health Check FAILED. Restarting Server..."
        Stop-Process -Name "python" -Force -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*onboarding_server.py*" }
        Start-Process $VenvPython -ArgumentList "$ServerScript" -WorkingDirectory $WorkDir -WindowStyle Hidden
        Start-Sleep -Seconds 10
    }

    # 3. Check Stable Tunnel (Cloudflare)
    $TunnelProcess = Get-Process -Name cloudflared -ErrorAction SilentlyContinue
    if (-not $TunnelProcess) {
        Write-Log "Stable Tunnel (Cloudflare) NOT found. Restarting..."
        Start-Process pwsh -ArgumentList "-File", "$WorkDir\scripts\start_stable_tunnel.ps1" -WorkingDirectory $WorkDir -WindowStyle Hidden
        Start-Sleep -Seconds 20 # Extended grace for tunnel stable URL generation
    }

    # 4. GitHub Update logic & Connectivity Verification
    try {
        if (Test-Path "data/tunnel.log") {
            $Lines = Get-Content "data/tunnel.log" -Tail 200 -ErrorAction SilentlyContinue
            if ($Lines) {
                $TunnelLog = $Lines -join "`n"
                $AllMatches = [regex]::Matches($TunnelLog, "https://[a-z0-9-]+\.trycloudflare\.com")
                if ($AllMatches.Count -gt 0) {
                    $CurrentUrl = $AllMatches[$AllMatches.Count - 1].Value
                    
                    # Update Redirects (Existing logic shortened for clarity in summary)
                    $Targets = @("onboarding/index.html", "onboarding/brain.html", "frontend/content_list.html", "index.md", "index.html", "onboard.html", "brain.html", "docs/index.html", "docs/onboard.html", "docs/brain.html")
                    $FilesChangedCount = 0
                    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss UTC"

                    foreach ($Target in $Targets) {
                        $FilePath = "$WorkDir\$Target"
                        if (Test-Path $FilePath) {
                            $Content = Get-Content $FilePath -Raw -ErrorAction SilentlyContinue
                            if ($null -eq $Content) { continue }
                            
                            $Pattern = '(var|const|let)\s+(githubOnboardingUrl|destination|targetUrl)\s*=\s*"([^"]*)";'
                            $Regex = [regex]$Pattern
                            $InnerMatch = $Regex.Match($Content)
                            
                            if ($InnerMatch.Success -and $InnerMatch.Groups[3].Value -ne $CurrentUrl) {
                                $NewContent = $Regex.Replace($Content, "$($InnerMatch.Groups[1].Value) $($InnerMatch.Groups[2].Value) = `"$CurrentUrl`";")
                                if ($Target -match "index|onboard|brain") {
                                    $NewContent = $NewContent -replace '<p id="updated".*?>.*?</p>', "<p id=`"updated`" style=`"font-size:0.8em; color:#64748b;`">Last Updated: $Timestamp</p>"
                                }
                                $NewContent | Set-Content -Path $FilePath -Encoding UTF8 -NoNewline
                                git add $FilePath
                                $FilesChangedCount++
                            }
                        }
                    }

                    if ($FilesChangedCount -gt 0) {
                        Write-Log "Pushing $FilesChangedCount updates to GitHub..."
                        git commit -m "System Sync: Monitoring active at $Timestamp"
                        git push
                    }

                    # 5. WinterHeartbite: Surgical Connectivity Check
                    Write-Log "WinterHeartbite: Verifying Local Tunnel..."
                    try {
                        $Response = Invoke-WebRequest -Uri $CurrentUrl -Method Get -TimeoutSec 10 -ErrorAction Stop
                        Write-Log "WinterHeartbite Success: Tunnel is truthfully alive."
                        $ConnectivityRetries = 0 # Reset counter on success
                    }
                    catch {
                        $ConnectivityRetries++
                        Write-Log "WINTERHEARTBITE FAILURE ($ConnectivityRetries/$MaxRetries): $_"
                        
                        if ($ConnectivityRetries -ge $MaxRetries) {
                            Write-Log "Max retries reached. Restarting Tunnel..."
                            Stop-Process -Name "cloudflared" -Force -ErrorAction SilentlyContinue
                            $ConnectivityRetries = 0
                        }
                    }
                }
            }
        }
    }
    catch { Write-Log "Monitoring loop error: $_" }

    Start-Sleep -Seconds 60
}
