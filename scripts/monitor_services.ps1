# Robust Monitor for Onboarding Server and Cloudflare Tunnel
# This script ensures both the intake server and the tunnel stay running all day.

# Set Terminal Title
$Host.UI.RawUI.WindowTitle = "[ SOVEREIGN WATCHDOG ]"

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
$IntegrityScript = "$WorkDir\scripts\verify_visual_integrity.py"
$SnapshotScript = "$WorkDir\scripts\generate_health_snapshots.py"

Write-Host "`n" + "="*60
Write-Host "  [ SOVEREIGN WATCHDOG ONLINE ]"
Write-Host "  `"Truth is not in numbers, but in the intention.`""
Write-Host "  Monitoring Onboarding Server & Tunnel..."
Write-Host "="*60 + "`n"

# 2. Defaults and Config Loading
$Config = @{
    HeartbeatTimeoutMin  = 5

    HeartbeatTimeoutMax  = 15
    MaxRetries           = 3
    RetryDelayMin        = 2
    RetryDelayMax        = 6
    CheckInterval        = 60
    SyncFiles            = @("index.html", "onboard.html", "brain.html")
    LogLevel             = "INFO"
    ProviderStack        = @("cloudflare", "localtunnel", "ngrok")
    CurrentProviderIndex = 0
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

Write-Host "VenvPython Path: $VenvPython"
Write-Host "ServerScript Path: $ServerScript"

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
    # Social alerting removed (Discord/Slack discarded).
    Write-Log "[ALERT] $Type — $Message" "INFO"
}

function Test-ConfigAgainstSchema($Cfg) {
    if ($null -eq $Cfg) { return $false }

    $Required = @("HeartbeatTimeoutMin", "HeartbeatTimeoutMax", "MaxRetries", "CheckInterval")
    foreach ($Prop in $Required) {
        if ($null -eq $Cfg.$Prop) { Write-Log "Schema Error: Missing required property '$Prop'" "WARN"; return $false }
    }

    # Range and Type Checks
    if ($Cfg.HeartbeatTimeoutMin -lt 1 -or $Cfg.HeartbeatTimeoutMin -gt 30) { Write-Log "Schema Error: HeartbeatTimeoutMin must be 1-30" "WARN"; return $false }
    # Handle both PSCustomObject and Hashtable (ConvertFrom-Json -AsHashtable vs default)
    $Max = $Cfg.HeartbeatTimeoutMax
    $Min = $Cfg.HeartbeatTimeoutMin
    if ($Max -le $Min) { Write-Log "Schema Error: HeartbeatTimeoutMax must be greater than Min" "WARN"; return $false }
    if ($Cfg.MaxRetries -lt 1 -or $Cfg.MaxRetries -gt 10) { Write-Log "Schema Error: MaxRetries must be 1-10" "WARN"; return $false }
    if ($Cfg.CheckInterval -lt 10) { Write-Log "Schema Error: CheckInterval must be >= 10s" "WARN"; return $false }
    
    return $true
}
function Get-ServiceHeartbeat($Url, $Name) {
    $MaxRetries = $Config['MaxRetries']
    for ($Attempt = 1; $Attempt -le $MaxRetries; $Attempt++) {
        $Timeout = Get-Random -Minimum $Config['HeartbeatTimeoutMin'] -Maximum ($Config['HeartbeatTimeoutMax'] + 1)
        Write-Log "Checking heartbeat for $($Name) at $Url (Attempt $Attempt/$MaxRetries, Timeout: ${Timeout}s)..."
        try {
            $Headers = @{ "bypass-tunnel-reminder" = "1" }
            $Response = Invoke-WebRequest -Uri $Url -Method Get -TimeoutSec $Timeout -Headers $Headers -ErrorAction Stop
            Write-Log "  [OK] $($Name) responded (Status: $($Response.StatusCode))"
            try {
                $Data = $Response.Content | ConvertFrom-Json
                if ($null -ne $Data.status) { Write-Log "  [SERVICE STATUS] $($Data.status)" "DEBUG" }
            }
            catch {
                Write-Log "  [WARN] Failed to parse JSON response from $($Name). Content: $($Response.Content.Substring(0, [Math]::Min(100, $Response.Content.Length)))" "WARN"
                return $false
            }
            return $true
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
        if (Get-ServiceHeartbeat -Url "http://127.0.0.1:5010/health" -Name "Onboarding Server (Local)") {
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

    # 2. Check Tunnel Health (Provider Agnostic)
    $TunnelProcess = Get-Process -Name cloudflared, lt, localtunnel -ErrorAction SilentlyContinue
    if (-not $TunnelProcess) {
        $TunnelProcess = Get-Process -Name node -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*localtunnel*" }
    }
    $TunnelLogPath = "$WorkDir\data\tunnel.log"
    $CurrentUrl = $null

    if (Test-Path "$WorkDir\.cloudflared\config.yml") {
        Write-Log "Named Tunnel Config detected. Extracting Sovereign hostname..." "DEBUG"
        $ConfigLines = Get-Content "$WorkDir\.cloudflared\config.yml" -Raw
        if ($ConfigLines -match "hostname:\s*([^\s\n\r]+)") {
            $CurrentUrl = "https://" + $Matches[1]
            Write-Log "  [SOVEREIGN] Permanent URL detected: $CurrentUrl" "INFO"
        }
    }

    if (-not $CurrentUrl -and (Test-Path $TunnelLogPath)) {
        $Lines = Get-Content $TunnelLogPath -Tail 200 -ErrorAction SilentlyContinue
        if ($Lines) {
            $TunnelLogStr = $Lines -join "`n"
            # Support Cloudflare, Localtunnel, and Ngrok patterns
            $Pattern = "https://([a-z0-9-]+\.trycloudflare\.com|[a-z0-9-]+\.loca\.lt|[a-z0-9-]+\.ngrok-free\.(app|dev))"
            $Match = [regex]::Match($TunnelLogStr, $Pattern)
            if ($Match.Success) {
                $AllMatches = [regex]::Matches($TunnelLogStr, $Pattern)
                $CurrentUrl = $AllMatches[$AllMatches.Count - 1].Value
            }
        }
    }

    if (-not $TunnelProcess -or -not $CurrentUrl) {
        $ActiveProvider = $Config.ProviderStack[$Config.CurrentProviderIndex]
        Write-Log "Tunnel Health Check FAILED (Process: $($null -ne $TunnelProcess), URL: $($null -ne $CurrentUrl)). Active Provider: $ActiveProvider" "WARN"
        
        # Determine if we should failover to the next provider
        if ($null -eq $global:TunnelFailCount) { $global:TunnelFailCount = 1 } else { $global:TunnelFailCount++ }
        
        if ($global:TunnelFailCount -gt 2) {
            $global:TunnelFailCount = 0
            $Config.CurrentProviderIndex = ($Config.CurrentProviderIndex + 1) % $Config.ProviderStack.Count
            $ActiveProvider = $Config.ProviderStack[$Config.CurrentProviderIndex]
            Write-Log "CRITICAL: Tunnel persistent failure. FAILING OVER to next provider: $ActiveProvider" "ERROR"
            Send-Alert "TUNNEL_FAILOVER" "Primary tunnel failed 3 times. Failing over to: $ActiveProvider"
        }

        Write-Log "Restarting tunnel using provider: $ActiveProvider..." "INFO"
        Send-Alert "TUNNEL_RESTART" "Attempting tunnel restart using provider: $ActiveProvider"
        
        # Kill any lingering tunnel processes before restart
        if ($TunnelProcess) { Stop-Process -Id $TunnelProcess.Id -Force -ErrorAction SilentlyContinue }
        
        Start-Process pwsh -ArgumentList "-File", "$WorkDir\scripts\start_stable_tunnel.ps1", "-Provider", $ActiveProvider -WorkingDirectory $WorkDir -WindowStyle Hidden
        Start-Sleep -Seconds 15
    }
    else {
        $global:TunnelFailCount = 0 # Reset fail count on healthy state
        Write-Log "Detected active tunnel URL ($($Config.ProviderStack[$Config.CurrentProviderIndex])): $CurrentUrl" "DEBUG"
    }

    # 3. Phase 6: Visual Integrity & Snapshot Generation
    Write-Log "Running Visual Integrity Check..." "DEBUG"
    & $VenvPython $IntegrityScript | Out-Null
    
    Write-Log "Generating Health Snapshot..." "DEBUG"
    & $VenvPython $SnapshotScript | Out-Null

    # 3. GitHub Update logic & Public Heartbeat
    try {
        if ($CurrentUrl) {
            # Public Heartbeat (verifies tunnel + server chain)
            if (-not (Get-ServiceHeartbeat -Url "$CurrentUrl/health" -Name "Public Tunnel Gateway")) {
                Write-Log "CRITICAL: Public Heartbeat failed. Forcing tunnel reset..." "ERROR"
                $CurrentUrl = $null
            }

            # 4. Update status.json (Dynamic Resolver)
            $StatusPath = "$WorkDir\data\status.json"
            $StatusData = @{
                last_updated = $Timestamp
                services     = @{
                    onboarding_server = @{
                        status     = "online"
                        local_url  = "http://127.0.0.1:5010"
                        public_url = $CurrentUrl
                    }
                    shahada_portal    = @{
                        status     = "online"
                        public_url = "$CurrentUrl/onboard"
                    }
                    brain_portal      = @{
                        status     = "online"
                        public_url = "$CurrentUrl/brain"
                    }
                }
                meta         = @{
                    provider        = $Config.ProviderStack[$Config.CurrentProviderIndex]
                    tunnel_id       = if ($CurrentUrl -match "loca.lt") { "manual-fallback" } elseif ($CurrentUrl -match "ngrok") { "ngrok-fallback" } else { "ephemeral-quick-tunnel" }
                    failover_active = ($Config.CurrentProviderIndex -gt 0)
                }
            }
            $StatusData | ConvertTo-Json -Depth 5 | Set-Content -Path $StatusPath -Encoding UTF8

            $FilesChangedCount = 0
            $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss UTC"

            git add -f $StatusPath
            $FilesChangedCount++

            $RedirectorTargets = $Config['SyncFiles']

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
                            
                    $Pattern = '(var|const|let)\s+(githubOnboardingUrl|destination|targetUrl)\s*=\s*"([^"]*)";'
                    $Regex = [regex]$Pattern
                    $InnerMatch = $Regex.Match($Content)
                            
                    if ($InnerMatch.Success -and -not [string]::IsNullOrEmpty($CurrentUrl)) {
                        if ($InnerMatch.Groups[3].Value -ne $CurrentUrl) {
                            $VarKeyword = $InnerMatch.Groups[1].Value
                            $VarName = $InnerMatch.Groups[2].Value
                            $NewContent = $Regex.Replace($NewContent, "$VarKeyword $VarName = `"$CurrentUrl`";")
                            $Changed = $true
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
                    git push origin HEAD:main
                    Send-Alert "SYNC_SUCCESS" "Status: Pushed $FilesChangedCount updates to GitHub Pages."
                }
                catch {
                    Write-Log "Git push failed: $($_.Exception.Message)" "ERROR"
                    Send-Alert "SYNC_FAILURE" "Error: Git push failed. Manual intervention required."
                }
            }
        }
    }
    catch {
        Write-Log "  [ERROR] Sync Logic Failure: $($_.Exception.Message)" "ERROR"
        Send-Alert "SYSTEM_ERROR" "Monitor experienced a loop error: $($_.Exception.Message)"
    }

    Start-Sleep -Seconds $Config['CheckInterval']
}
