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
        Start-Sleep -Seconds 15
        $TunnelProcess = Get-Process -Name cloudflared -ErrorAction SilentlyContinue
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
                                if ($InnerMatch.Groups[3].Value -ne $CurrentUrl) {
                                    $VarKeyword = $InnerMatch.Groups[1].Value
                                    $VarName = $InnerMatch.Groups[2].Value
                                    $NewContent = $Regex.Replace($NewContent, "$VarKeyword $VarName = `"$CurrentUrl`";")
                                    $Changed = $true
                                }
                            }
                            
                            # Also update timestamp for redirectors ONLY if something else changed
                            if ($Changed -and ($NewContent -match '<p id="updated".*?>.*?</p>')) {
                                $NewContent = $NewContent -replace '<p id="updated".*?>.*?</p>', "<p id=`"updated`" style=`"font-size:0.8em; color:#64748b;`">Last Updated: $Timestamp</p>"
                            }

                            if ($Changed) {
                                $NewContent | Set-Content -Path $FilePath -Encoding UTF8 -NoNewline
                                git add $FilePath
                                $FilesChangedCount++
                                Write-Log "Queued update for $Target -> $CurrentUrl"
                            }
                        }
                    }

                    if ($FilesChangedCount -gt 0) {
                        Write-Log "Pushing $FilesChangedCount updates to GitHub..."
                        git commit -m "System Sync: Monitoring active at $Timestamp"
                        git push
                    }

                    # 4. WinterHeartbite: Direct API Interrogation (The Biting Truth)
                    try {
                        $MissionPillars = @(
                            "winter-relief-for-rana-and-her-seven-children-",
                            "-urgent-winter-aid-for-mother-of-10"
                        )
                        
                        Write-Log "WinterHeartbite: Interrogating Mission Pillars..."
                        
                        foreach ($Slug in $MissionPillars) {
                            $ApiUrl = "https://fundraiser.whydonate.dev/fundraiser/get?slug=$Slug&language=en"
                            try {
                                $ApiResponse = Invoke-RestMethod -Uri $ApiUrl -Method Get -TimeoutSec 10 -ErrorAction Stop
                                
                                # WhyDonate API returns 200 OK even for errors, check the internal 'errors' field
                                if ($null -ne $ApiResponse.data.errors) {
                                    $ErrMsg = $ApiResponse.data.errors.message
                                    throw "MISSION DECEPTION DETECTED on $($Slug): $ErrMsg"
                                }
                                
                                # Verify the result object exists and has content
                                if ($null -eq $ApiResponse.data.result -or $null -eq $ApiResponse.data.result.id) {
                                    throw "MISSION VOID DETECTED on $($Slug): API returned empty result."
                                }
                                
                                Write-Log "  Pillar $Slug is LIVE (ID: $($ApiResponse.data.result.id))"
                            }
                            catch {
                                throw "Pillar Interrogation Failure ($Slug): $_"
                            }
                        }

                        # Also check the local tunnel for basic connectivity
                        Write-Log "WinterHeartbite: Verifying Local Tunnel..."
                        $Response = Invoke-WebRequest -Uri $CurrentUrl -Method Get -TimeoutSec 10 -ErrorAction Stop
                        Write-Log "WinterHeartbite Success: Mission and Tunnel are truthfully alive."
                    }
                    catch {
                        Write-Log "WINTERHEARTBITE FAILURE: $_"
                        Write-Log "Executing systemic interruption (Purging and Restarting)..."
                        Stop-Process -Name "cloudflared" -Force -ErrorAction SilentlyContinue
                        Stop-Process -Name "python" -Force -ErrorAction SilentlyContinue
                        Start-Sleep -Seconds 5
                    }
                }
            }
        }
    }
    catch { Write-Log "Monitoring loop error: $_" }

    Start-Sleep -Seconds 60
}
