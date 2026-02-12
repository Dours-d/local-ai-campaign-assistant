$inventory = Import-Csv -Path 'c:\Users\gaelf\Documents\GitHub\local_ai_campaign_assistant\screenshot_inventory.csv'
$filtered = $inventory | Where-Object { 
    [int]$_.Length -gt 60000 -and 
    [int]$_.Length -lt 100000 -and 
    $_.Name -like 'Capture*' -and
    ($_.Name -like '*2024-01*' -or $_.Name -like '*2024-02*' -or $_.Name -like '*2024-03*' -or $_.Name -like '*2024-04*')
} | Sort-Object LastWriteTime

$filtered.Name | Out-File -FilePath 'c:\Users\gaelf\Documents\GitHub\local_ai_campaign_assistant\candidate_snapshots.txt'
