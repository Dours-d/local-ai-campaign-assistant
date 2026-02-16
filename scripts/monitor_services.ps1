# Robust Monitor for Onboarding Server and Cloudflare Tunnel
# This script ensures both the intake server and the tunnel stay running all day.

$LogFile = "data/monitoring.log"
$WorkDir = Get-Location
$ServerScript = "scripts/onboarding_server.py"
$VenvPython = "$WorkDir\.venv\Scripts\python.exe"

function Write-Log($Message) {
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "[$Timestamp] $Message"
    Write-Host $LogEntry -ForegroundColor Cyan
    if (-not (Test-Path "data")) { New-Item -ItemType Directory -Path "data" -Force }
    $LogEntry | Out-File -FilePath $LogFile -Append
}

Write-Log "Starting Final Monitor Service v4..."

while ($true) {
    # 1. Check Onboarding Server
    $ServerProcess = Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*onboarding_server.py*" }
    if (-not $ServerProcess) {
        Write-Log "Onboarding Server NOT found. Restarting..."
        Start-Process $VenvPython -ArgumentList "$ServerScript" -WorkingDirectory $WorkDir -WindowStyle Hidden
    }

    # 2. Check Stable Tunnel (Cloudflare)
    $TunnelProcess = Get-Process -Name cloudflared -ErrorAction SilentlyContinue
    if (-not $TunnelProcess) {
        Write-Log "Stable Tunnel (Cloudflare) NOT found. Restarting..."
        Start-Process pwsh -ArgumentList "-File", "$WorkDir\scripts\start_stable_tunnel.ps1" -WorkingDirectory $WorkDir -WindowStyle Hidden
        Start-Sleep -Seconds 10
    }

    # 3. GitHub Update logic
    try {
        if (Test-Path "data/tunnel.log") {
            # Use -Tail 200 and then join to avoid -Raw conflict
            $Lines = Get-Content "data/tunnel.log" -Tail 200 -ErrorAction SilentlyContinue
            if ($Lines) {
                $TunnelLog = $Lines -join "`n"
                $Match = [regex]::Match($TunnelLog, "https://[a-z0-9-]+\.trycloudflare\.com")
                if ($Match.Success) {
                    # Get the LAST match in case multiple tunnels appear in the tail
                    $AllMatches = [regex]::Matches($TunnelLog, "https://[a-z0-9-]+\.trycloudflare\.com")
                    $CurrentUrl = $AllMatches[$AllMatches.Count - 1].Value
                    
                    $TunnelTargets = @("onboarding/index.html", "onboarding/brain.html")
                    $VercelUrl = "https://local-ai-campaign-assistant.vercel.app"
                    $RedirectorTargets = @("index.md", "index.html", "onboard.html", "brain.html", "docs/index.html", "docs/onboard.html", "docs/brain.html")

                    $FilesChangedCount = 0
                    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss UTC"

                    # Update Tunnel Targets (point to Cloudflare)
                    foreach ($Target in $TunnelTargets) {
                        $FilePath = "$WorkDir\$Target"
                        if (Test-Path $FilePath) {
                            $Content = Get-Content $FilePath -Raw -ErrorAction SilentlyContinue
                            if ([string]::IsNullOrWhiteSpace($Content)) {
                                $Content = (Get-Content $FilePath) -join "`r`n"
                            }
                            
                            $Pattern = '(var|const|let)\s+(githubOnboardingUrl|destination|targetUrl)\s*=\s*"([^"]*)";'
                            $Regex = [regex]$Pattern
                            $InnerMatch = $Regex.Match($Content)
                            
                            if ($InnerMatch.Success) {
                                if ($InnerMatch.Groups[3].Value -ne $CurrentUrl) {
                                    $VarKeyword = $InnerMatch.Groups[1].Value
                                    $VarName = $InnerMatch.Groups[2].Value
                                    $NewContent = $Regex.Replace($Content, "$VarKeyword $VarName = `"$CurrentUrl`";")
                                    $NewContent | Set-Content -Path $FilePath -Encoding UTF8 -NoNewline
                                    git add $FilePath
                                    $FilesChangedCount++
                                    Write-Log "Queued update for $Target -> $CurrentUrl"
                                }
                            }
                        }
                    }

                    # Update Redirector Targets (point to Vercel)
                    foreach ($Target in $RedirectorTargets) {
                        $FilePath = "$WorkDir\$Target"
                        if (Test-Path $FilePath) {
                            $Content = Get-Content $FilePath -Raw -ErrorAction SilentlyContinue
                            if ([string]::IsNullOrWhiteSpace($Content)) {
                                $Content = (Get-Content $FilePath) -join "`r`n"
                            }
                            
                            $Changed = $false
                            $NewContent = $Content
                            
                            $Pattern = '(var|const|let)\s+(githubOnboardingUrl|destination|targetUrl)\s*=\s*"([^"]*)";'
                            $Regex = [regex]$Pattern
                            $InnerMatch = $Regex.Match($Content)
                            
                            if ($InnerMatch.Success) {
                                if ($InnerMatch.Groups[3].Value -ne $VercelUrl) {
                                    $VarKeyword = $InnerMatch.Groups[1].Value
                                    $VarName = $InnerMatch.Groups[2].Value
                                    $NewContent = $Regex.Replace($NewContent, "$VarKeyword $VarName = `"$VercelUrl`";")
                                    $Changed = $true
                                }
                            }
                            
                            # Also update timestamp for redirectors
                            if ($NewContent -match '<p id="updated".*?>.*?</p>') {
                                $NewContent = $NewContent -replace '<p id="updated".*?>.*?</p>', "<p id=`"updated`" style=`"font-size:0.8em; color:#64748b;`">Last Updated: $Timestamp</p>"
                                $Changed = $true
                            }

                            if ($Changed) {
                                $NewContent | Set-Content -Path $FilePath -Encoding UTF8 -NoNewline
                                git add $FilePath
                                $FilesChangedCount++
                                Write-Log "Queued update for $Target -> $VercelUrl"
                            }
                        }
                    }

                    if ($FilesChangedCount -gt 0) {
                        Write-Log "Pushing $FilesChangedCount updates to GitHub..."
                        git commit -m "System Sync: Monitoring active at $Timestamp"
                        git push
                    }
                }
            }
        }
    }
    catch { Write-Log "GitHub Update failure: $_" }

    Start-Sleep -Seconds 60
}
