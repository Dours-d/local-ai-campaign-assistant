
$TunnelLog = Get-Content "data/tunnel.log" -Tail 200
$AllMatches = $TunnelLog | Select-String -Pattern "https://[a-z0-9-]+\.trycloudflare\.com" -AllMatches
if ($AllMatches) {
    Write-Host "Found matches: $($AllMatches.Count)"
    $CurrentUrl = $AllMatches[-1].Matches.Value
    Write-Host "Latest URL: $CurrentUrl"
}
else {
    Write-Host "No matches found."
}
