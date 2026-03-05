# Robust Monitor for Onboarding Server and Cloudflare Tunnel
# This script ensures both the intake server and the tunnel stay running all day.

param(
    [int]$HeartbeatTimeoutMin,
    [int]$HeartbeatTimeoutMax,
    [int]$MaxRetries,
    [int]$RetryDelayMin,
    [int]$RetryDelayMax,
    [int]$CheckInterval,
    [string[]]$SyncFiles
)

# 1. Environment & Paths
$WorkDir = "c:\Users\gaelf\Documents\GitHub\local_ai_campaign_assistant"
$VenvPython = "$WorkDir\.venv\Scripts\python.exe"
$ServerScript = "$WorkDir\scripts\onboarding_server.py"
$LogFile = "$WorkDir\data\monitoring.log"
$ConfigFile = "$WorkDir\scripts\monitor_config.json"

# 2. Defaults and Config Loading
$Config = @{
    HeartbeatTimeoutMin = 5
    HeartbeatTimeoutMax = 15
    MaxRetries          = 3
    RetryDelayMin       = 2
    RetryDelayMax       = 6
    CheckInterval       = 60
    SyncFiles           = @("index.html", "onboard.html", "brain.html", "campaigns.html", "docs\index.html", "docs\brain.html", "frontend\index.html", "frontend\campaigns.html", "onboarding\brain.html", "onboarding\index.html", "onboarding\onboard.html")
    LogLevel            = "INFO"
    Alerting            = @{
        Enabled         = $false
        CooldownMinutes = 5
        LastSent        = @{}
        SuppressedCount = 0 # Metrics for SEO/Trustee visibility
    }
}

function Write-Log($Message, $Level = "INFO") {
    if ($null -eq $Message) { return }
    # Simple level filtering
    if ($Config.LogLevel -eq "INFO" -and $Level -eq "DEBUG") { return }
    
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogLine = "[$Timestamp] [$Level] $Message"
    Write-Host $LogLine
    try {
        if (-not (Test-Path (Split-Path $LogFile -Parent))) { New-Item -ItemType Directory -Path (Split-Path $LogFile -Parent) -Force | Out-Null }
        $LogLine | Out-File -FilePath $LogFile -Append -Encoding UTF8
    }
    catch {}
}

function Import-Env($Path) {
    if (Test-Path $Path) {
        Write-Log "Loading environment from $Path" "DEBUG"
        Get-Content $Path | ForEach-Object {
            if ($_ -match '^([^#=]+)\s*=\s*"?([^#"]*)"?') {
                [Environment]::SetEnvironmentVariable($Matches[1].Trim(), $Matches[2].Trim())
            }
        }
    }
}

function Send-Alert($Type, $Message) {
    if (-not $Config.Alerting.Enabled) { return }
    
    $DiscordUrl = [Environment]::GetEnvironmentVariable("MONITOR_DISCORD_WEBHOOK")
    $SlackUrl = [Environment]::GetEnvironmentVariable("MONITOR_SLACK_WEBHOOK")

    if (-not ($DiscordUrl -or $SlackUrl)) { return }

    # Initialize internal state if missing
    if ($null -eq $Config.Alerting.LastSent) {
        if ($Config.Alerting -is [System.Management.Automation.PSCustomObject]) { $Config.Alerting | Add-Member -MemberType NoteProperty -Name "LastSent" -Value @{} -Force }
        else { $Config.Alerting["LastSent"] = @{} }
    }
    
    # Cooldown check
    $LastSent = $Config.Alerting.LastSent[$Type]
    if ($null -ne $LastSent) {
        if ((Get-Date) -lt $LastSent.AddMinutes($Config.Alerting.CooldownMinutes)) {
            $Config.Alerting.SuppressedCount++
            Write-Log "Alert '$Type' skipped (Cooldown active). Total suppressed: $($Config.Alerting.SuppressedCount)" "DEBUG"
            return
        }
    }

    # Severity Coloring & Meta
    $Color = 3066993 # Default Green
    $SlackColor = "#36a64f"
    if ($Type -match "FAILURE|ERROR") { $Color = 15158332; $SlackColor = "#ff0000" }
    elseif ($Type -match "ATTEMPT|RESTART") { $Color = 16776960; $SlackColor = "#eed202" }

    # 1. Discord Embed Payload
    $DiscordBody = @{
        embeds = @(@{
                title       = "Monitor Alert: $Type"
                description = $Message
                color       = $Color
                timestamp   = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
                footer      = @{ text = "Local AI Campaign Assistant | Final Monitor v5.5" }
            })
    } | ConvertTo-Json -Depth 5

    # 2. Slack Block Payload
    $SlackBody = @{
        attachments = @(@{
                color  = $SlackColor
                blocks = @(
                    @{
                        type = "section"
                        text = @{ type = "mrkdwn"; text = "*Monitor Alert: $Type*`n$Message" }
                    },
                    @{
                        type     = "context"
                        elements = @(@{ type = "mrkdwn"; text = "Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" })
                    }
                )
            })
    } | ConvertTo-Json -Depth 5

    if ($DiscordUrl) {
        try {
            Invoke-RestMethod -Uri $DiscordUrl -Method Post -ContentType "application/json" -Body $DiscordBody -ErrorAction Stop
            Write-Log "Rich Alert sent to Discord: $Type" "DEBUG"
        }
        catch { Write-Log "Failed to send Discord alert: $($_.Exception.Message)" "WARN" }
    }
    
    if ($SlackUrl) {
        try {
            Invoke-RestMethod -Uri $SlackUrl -Method Post -ContentType "application/json" -Body $SlackBody -ErrorAction Stop
            Write-Log "Rich Alert sent to Slack: $Type" "DEBUG"
        }
        catch { Write-Log "Failed to send Slack alert: $($_.Exception.Message)" "WARN" }
    }

    $Config.Alerting.LastSent[$Type] = Get-Date
}

function Test-ConfigAgainstSchema($Cfg) {
    if ($null -eq $Cfg) { return $false }

    $SchemaPath = Join-Path $WorkDir "scripts\monitor_schema.json"
    if (Test-Path $SchemaPath) {
        Write-Log "Validating config against $SchemaPath" "DEBUG"
        # In a real environment, we might use a PowerShell JSON Schema validator module
        # but for now, we'll perform a strict manual validation based on the schema definition.
    }

    $Required = @("HeartbeatTimeoutMin", "HeartbeatTimeoutMax", "MaxRetries", "CheckInterval", "Alerting")
    foreach ($Prop in $Required) {
        if ($null -eq $Cfg.$Prop) { Write-Log "Schema Error: Missing required property '$Prop'" "WARN"; return $false }
    }

    # Range and Type Checks (Aligned with monitor_schema.json)
    if ($Cfg.HeartbeatTimeoutMin -lt 1 -or $Cfg.HeartbeatTimeoutMin -gt 30) { Write-Log "Schema Error: HeartbeatTimeoutMin must be 1-30" "WARN"; return $false }
    if ($Cfg.HeartbeatTimeoutMax -lt 1 -or $Cfg.HeartbeatTimeoutMax -gt 60) { Write-Log "Schema Error: HeartbeatTimeoutMax must be 1-60" "WARN"; return $false }
    
    $Max = $Cfg.HeartbeatTimeoutMax
    $Min = $Cfg.HeartbeatTimeoutMin
    if ($Max -le $Min) { Write-Log "Schema Error: HeartbeatTimeoutMax ($Max) must be greater than Min ($Min)" "WARN"; return $false }
    
    if ($Cfg.MaxRetries -lt 1 -or $Cfg.MaxRetries -gt 10) { Write-Log "Schema Error: MaxRetries must be 1-10" "WARN"; return $false }
    if ($Cfg.CheckInterval -lt 10) { Write-Log "Schema Error: CheckInterval must be >= 10s" "WARN"; return $false }
    
    if ($null -eq $Cfg.Alerting.Enabled) {
        Write-Log "Schema Error: Missing Alerting.Enabled" "WARN"; return $false
    }

    if ($Cfg.Alerting.Enabled) {
        if ($null -eq $Cfg.Alerting.Endpoints) {
            Write-Log "Schema Error: Missing Alerting.Endpoints for enabled alerting" "WARN"; return $false
        }
        if ($null -eq $Cfg.Alerting.Endpoints.DiscordEnvVar -or $null -eq $Cfg.Alerting.Endpoints.SlackEnvVar) {
            Write-Log "Schema Error: Incomplete Alerting.Endpoints" "WARN"; return $false
        }
    }
    
    return $true
}
# Load secrets
Import-Env "$WorkDir\.env.monitoring"

if (Test-Path $ConfigFile) {
    try {
        $RawConfig = Get-Content $ConfigFile -Raw
        $FileConfig = $RawConfig | ConvertFrom-Json
        
        if (Test-ConfigAgainstSchema $FileConfig) {
            foreach ($Key in @($Config.Keys)) {
                if ($null -ne $FileConfig.$Key) { 
                    $Config[$Key] = $FileConfig.$Key 
                    Write-Log "  [CONFIG] Merged $Key" "DEBUG"
                }
            }
            Write-Log "Configuration validated and loaded from $ConfigFile" "DEBUG"
        }
        else {
            Write-Log "Configuration in $ConfigFile failed schema validation. Using defaults." "WARN"
        }
    }
    catch { 
        Write-Log "Failed to parse ${ConfigFile}: $($_.Exception.Message)" "WARN" 
        Write-Log "Raw Content Snippet: $($RawConfig.Substring(0, [Math]::Min(50, $RawConfig.Length)))" "DEBUG"
    }
}

# 3. CLI Overrides
if ($PSBoundParameters.ContainsKey('HeartbeatTimeoutMin')) { $Config['HeartbeatTimeoutMin'] = $HeartbeatTimeoutMin }
if ($PSBoundParameters.ContainsKey('HeartbeatTimeoutMax')) { $Config['HeartbeatTimeoutMax'] = $HeartbeatTimeoutMax }
if ($PSBoundParameters.ContainsKey('MaxRetries')) { $Config['MaxRetries'] = $MaxRetries }
if ($PSBoundParameters.ContainsKey('RetryDelayMin')) { $Config['RetryDelayMin'] = $RetryDelayMin }
if ($PSBoundParameters.ContainsKey('RetryDelayMax')) { $Config['RetryDelayMax'] = $RetryDelayMax }
if ($PSBoundParameters.ContainsKey('CheckInterval')) { $Config['CheckInterval'] = $CheckInterval }
if ($PSBoundParameters.ContainsKey('SyncFiles')) { $Config['SyncFiles'] = $SyncFiles }

# 3. Identity Calculation (Architectural Persistence)
function Get-ExpectedNodeId {
    $Seed = [Environment]::GetEnvironmentVariable("ADMIN_SECRET_KEY")
    if ($null -eq $Seed) { $Seed = "sovereign_fallback_key_123" }
    
    $Raw = "noor-brain-$Seed"
    $Sha = [System.Security.Cryptography.SHA256]::Create()
    $Bytes = [System.Text.Encoding]::UTF8.GetBytes($Raw)
    $Hash = $Sha.ComputeHash($Bytes)
    $Hex = ($Hash | ForEach-Object { $_.ToString("x2") }) -join ""
    return $Hex.Substring(0, 16)
}

$ExpectedNodeId = Get-ExpectedNodeId
Write-Log "  NODE IDENTITY INITIALIZED: $ExpectedNodeId" "INFO"

function Get-ServiceHeartbeat($Url, $Name, [string]$RequiredNodeId = $null) {
    $MaxRetries = $Config['MaxRetries']
    for ($Attempt = 1; $Attempt -le $MaxRetries; $Attempt++) {
        $Timeout = Get-Random -Minimum $Config['HeartbeatTimeoutMin'] -Maximum ($Config['HeartbeatTimeoutMax'] + 1)
        Write-Log "Checking heartbeat for $($Name) at $Url (Attempt $Attempt/$MaxRetries, Timeout: ${Timeout}s)..."
        try {
            $Response = Invoke-WebRequest -Uri $Url -Method Get -TimeoutSec $Timeout -ErrorAction Stop
            
            # Identity Verification (High-Level Manifestation)
            try {
                $Data = $Response.Content | ConvertFrom-Json
                if ($null -ne $RequiredNodeId) {
                    if ($Data.node_id -eq $RequiredNodeId) {
                        Write-Log "  [OK] $($Name) Identity Verified: $($Data.node_id)" "INFO"
                        return $true
                    } else {
                        Write-Log "  [SECURITY ALERT] $($Name) Identity Mismatch! Expected: $RequiredNodeId, Found: $($Data.node_id)" "WARN"
                        # This identifies a Tunnel Interstitial or Hijack
                        return $false 
                    }
                }
                
                # Fallback: Success if status is 200 (Legacy/Simple endpoints)
                Write-Log "  [OK] $($Name) responded (Status: $($Response.StatusCode))"
                return $true
            }
            catch {
                # Resilience: Status 200 is success if no specific ID is required
                if ($null -eq $RequiredNodeId) {
                    Write-Log "  [OK] $($Name) responded 200 (JSON parse failed, but status preserved)." "DEBUG"
                    return $true
                }
                Write-Log "  [WARN] Failed to parse JSON identity from $($Name). Endpoint likely blocked." "WARN"
                return $false
            }
        }
        catch {
            Write-Log "  [WARN] Attempt $Attempt failed for $($Name): $($_.Exception.Message)"
            if ($Attempt -lt $MaxRetries) {
                $Delay = Get-Random -Minimum $Config['RetryDelayMin'] -Maximum ($Config['RetryDelayMax'] + 1)
                Start-Sleep -Seconds $Delay
            }
        }
    }
    Write-Log "  [CRITICAL] All $MaxRetries heartbeat attempts FAILED for $($Name)." "WARN"
    Send-Alert "HEARTBEAT_FAILURE" "Service: $Name`nEndpoint: $Url`nStatus: FAILED after $MaxRetries attempts."
    return $false
}

Write-Log "Starting Final Monitor Service v5.4 (Alerting & Configuration Edition)..."
Write-Log "Config in use: $($Config | ConvertTo-Json -Compress)" "DEBUG"

while ($true) {
    # 1. Check Onboarding Server (Process + Heartbeat)
    $ServerProcess = Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*onboarding_server.py*" }
    $ServerAlive = $false
    if ($ServerProcess) {
        if (Get-ServiceHeartbeat -Url "http://127.0.0.1:5010/health" -Name "Onboarding Server (Local)" -RequiredNodeId $ExpectedNodeId) {
            $ServerAlive = $true
        }
    }

    if (-not $ServerAlive) {
        Write-Log "Onboarding Server NOT responsive or NOT found. Attempting controlled restart..." "WARN"
        $Cmd = "$VenvPython $ServerScript"
        Write-Log "  [RESTART] Initializing restart: $Cmd" "INFO"
        Send-Alert "RESTART_ATTEMPT" "Service: Onboarding Server`nAction: Initiating restart via $VenvPython."
        
        try {
            if ($ServerProcess) { 
                Write-Log "  Stopping existing unresponsive process ID: $($ServerProcess.Id)" "DEBUG"
                Stop-Process -Id $ServerProcess.Id -Force -ErrorAction SilentlyContinue 
            }
            Start-Process $VenvPython -ArgumentList "$ServerScript" -WorkingDirectory $WorkDir -WindowStyle Hidden -ErrorAction Stop
            Write-Log "  [SUCCESS] Restart command executed successfully at $(Get-Date)." "INFO"
            Send-Alert "RESTART_SUCCESS" "Service: Onboarding Server`nStatus: Restart command issued successfully."
        }
        catch {
            Write-Log "  [ERROR] Failed to execute restart: $($_.Exception.Message)" "ERROR"
            Send-Alert "RESTART_FAILURE" "Service: Onboarding Server`nError: $($_.Exception.Message)"
        }
        Start-Sleep -Seconds 5
    }

    # 2. Check Stable Tunnel (Cloudfare)
    $TunnelProcess = Get-Process -Name cloudflared -ErrorAction SilentlyContinue
    if (-not $TunnelProcess) {
        Write-Log "Stable Tunnel (Cloudflare) NOT found. Restarting..." "WARN"
        Send-Alert "TUNNEL_RESTART" "Cloudflare tunnel process not found. Restarting..."
        Start-Process pwsh -ArgumentList "-File", "$WorkDir\scripts\start_stable_tunnel.ps1" -WorkingDirectory $WorkDir -WindowStyle Hidden
        Start-Sleep -Seconds 15
    }

    # 3. GitHub Update logic & Public Heartbeat
    try {
        if (Test-Path "data/tunnel.log") {
            $Lines = Get-Content "data/tunnel.log" -Tail 200 -ErrorAction SilentlyContinue
            if ($Lines) {
                $TunnelLog = $Lines -join "`n"
                $Match = [regex]::Match($TunnelLog, "https://[a-z0-9-]+\.trycloudflare\.com")
                if ($Match.Success) {
                    $AllMatches = [regex]::Matches($TunnelLog, "https://[a-z0-9-]+\.trycloudflare\.com")
                    $CurrentUrl = $AllMatches[$AllMatches.Count - 1].Value
                    
                    # Public Heartbeat (verifies tunnel + server chain + identity)
                    Get-ServiceHeartbeat -Url "$CurrentUrl/health" -Name "Public Tunnel Gateway" -RequiredNodeId $ExpectedNodeId | Out-Null

                    $RedirectorTargets = $Config['SyncFiles']
                    if ([string]::IsNullOrWhiteSpace($CurrentUrl)) {
                        Write-Log "  [SKIP] Current URL is empty, skipping sync." "DEBUG"
                        continue
                    }

                    $FilesChangedCount = 0
                    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss UTC"

                    # Update Redirector Targets (point to Vercel/GitHub Pages redirector)
                    foreach ($Target in $RedirectorTargets) {
                        $FilePath = "$WorkDir\$Target"
                        if (Test-Path $FilePath) {
                            $Content = Get-Content $FilePath -Raw -ErrorAction SilentlyContinue
                            if ([string]::IsNullOrWhiteSpace($Content)) {
                                $Content = (Get-Content $FilePath) -join "`r`n"
                            }
                            
                            $Changed = $false
                            $NewContent = $Content
                            
                            # Robust Pattern: Matches var|const|let|window.NAME = "..." OR {{ targetUrl }} OR TARGET_URL_PLACEHOLDER = "..." OR JSON "public_url": "..."
                            $Patterns = @(
                                '(?m)(var|const|let|window\.)\s*(githubOnboardingUrl|destination|targetUrl|TARGET_URL_PLACEHOLDER)\s*=\s*"([^"]*)";?',
                                '\{\{\s*(targetUrl)\s*\}\}',
                                '"public_url":\s*"([^"]*)"'
                            )

                            foreach ($P in $Patterns) {
                                try {
                                    $Regex = [regex]::new($P, [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)
                                    $MatchColl = $Regex.Matches($NewContent)
                                    foreach ($M in $MatchColl) {
                                        # Group logic: 
                                        # 1. Var/Const: Group 3 is the value
                                        # 2. Mustache: Match is the value (no groups)
                                        # 3. JSON: Group 1 is the value
                                        $OldValue = if ($M.Groups.Count -gt 3) { $M.Groups[3].Value } elseif ($M.Groups.Count -gt 1) { $M.Groups[1].Value } else { $M.Value }
                                        
                                        if ($OldValue -ne $CurrentUrl) {
                                            if ($P -like "*\{\{*") {
                                                $NewContent = $NewContent.Replace($M.Value, $CurrentUrl)
                                            } elseif ($P -match '"public_url"') {
                                                $NewValue = "`"public_url`": `"$CurrentUrl`""
                                                $NewContent = $NewContent.Replace($M.Value, $NewValue)
                                            } else {
                                                $VarKeyword = $M.Groups[1].Value
                                                $VarName = $M.Groups[2].Value
                                                $NewValue = "$VarKeyword $VarName = `"$CurrentUrl`";"
                                                $NewContent = $NewContent.Replace($M.Value, $NewValue)
                                            }
                                            $Changed = $true
                                        }
                                    }
                                } catch {
                                    Write-Log "Regex failure on pattern $P: $($_.Exception.Message)" "DEBUG"
                                }
                            }
                            
                            if ($Changed -and ($NewContent -match '<p id="updated".*?>.*?</p>')) {
                                $NewContent = $NewContent -replace '<p id="updated".*?>.*?</p>', "<p id=`"updated`" style=`"font-size:0.8em; color:#64748b;`">Last Updated: $Timestamp</p>"
                            }

                            if ($Changed) {
                                $NewContent | Set-Content -Path $FilePath -Encoding UTF8 -NoNewline
                                git add $FilePath
                                $FilesChangedCount++
                                Write-Log "Queued sync for $Target -> $CurrentUrl" "INFO"
                            }
                        }
                    }

                    if ($FilesChangedCount -gt 0) {
                        Write-Log "Pushing $FilesChangedCount critical updates to GitHub..." "INFO"
                        try {
                            git commit -m "System Sync: Persistent gateway at $Timestamp"
                            git push
                            
                            # START: High-Level Edge Verification (Architectural Habit)
                            Write-Log "--- High-Level Edge Verification Triggered ---" "INFO"
                            $MaxEdgeAttempts = 12
                            $EdgeWaitSeconds = 20 # Increased for GitHub CDN reliability
                            $PublicJsonUrl = "https://raw.githubusercontent.com/Dours-d/local-ai-campaign-assistant/main/data/status.json"
                            
                            $EdgeSuccess = $false
                            for ($i = 1; $i -le $MaxEdgeAttempts; $i++) {
                                Write-Log "[EDGE VERIFY $i/$MaxEdgeAttempts] Polling public truth manifestation..." "INFO"
                                try {
                                    # Cache busting via timestamp
                                    $Tick = [DateTimeOffset]::Now.ToUnixTimeSeconds()
                                    $EdgeResponse = Invoke-RestMethod -Uri "$PublicJsonUrl?t=$Tick" -Method Get -TimeoutSec 10
                                    $EdgeUrl = $EdgeResponse.services.onboarding_server.public_url
                                    
                                    if ($EdgeUrl -eq $CurrentUrl) {
                                        Write-Log "[SUCCESS] Public edge truth manifested: $EdgeUrl" "INFO"
                                        $EdgeSuccess = $true
                                        break
                                    } else {
                                        Write-Log "  [STALE] Edge still lagging. Found: $EdgeUrl" "DEBUG"
                                    }
                                } catch {
                                    Write-Log "  [WARN] Edge poll error: $($_.Exception.Message)" "DEBUG"
                                }
                                Start-Sleep -Seconds $EdgeWaitSeconds
                            }
                            
                            if ($EdgeSuccess) {
                                Send-Alert "SYNC_VERIFIED" "Status: Pushed and VERIFIED $FilesChangedCount updates. Public edge is live."
                            } else {
                                Write-Log "[WARN] Pushed successfully, but edge propagation is still lagging beyond $MaxEdgeAttempts attempts." "WARN"
                                Send-Alert "SYNC_STALE" "Status: Pushed $FilesChangedCount updates, but PUBLIC EDGE IS STILL STALE. Monitoring continues."
                            }
                            # END: High-Level Edge Verification
                        }
                        catch {
                            Write-Log "Git push failed: $($_.Exception.Message)" "ERROR"
                            Send-Alert "SYNC_FAILURE" "Error: Git push failed. Manual intervention required."
                        }
                    }
                }
            }
        }
    }
    catch {
        Write-Log "  [ERROR] Sync Logic Failure: $($_.Exception.Message)" "ERROR"
        Send-Alert "SYSTEM_ERROR" "Monitor experienced a loop error: $($_.Exception.Message)"
    }

    # 4. Probabilistic Chaos (Realistic Jitter - 1% chance)
    if ((Get-Random -Minimum 0 -Maximum 100) -lt 1) {
        Write-Log "[CHAOS] Triggering probabilistic jitter event (Simulated Transient Failure)..." "WARN"
        Send-Alert "CHAOS_JITTER" "Status: Probabilistic jitter event triggered. Testing system resilience."
        Start-Sleep -Seconds 2 # Simulating a brief delay/hiccup
    }

    Start-Sleep -Seconds $Config['CheckInterval']
}
