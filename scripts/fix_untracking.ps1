# fix_untracking.ps1
# This script resolves the issue where antigravity-auto-accept is not tracked by the root repository
# because it contains its own .git folder (nested repository).

$RepoRoot = "c:\Users\gaelf\Documents\GitHub\local_ai_campaign_assistant"
$TargetDir = "$RepoRoot\antigravity-auto-accept"

Write-Host "Resolving untracking for $TargetDir..." -ForegroundColor Green

# 1. Check if the .git folder exists in the target directory
if (Test-Path "$TargetDir\.git") {
    Write-Host "Removing nested .git directory..." -ForegroundColor Yellow
    Remove-Item -Path "$TargetDir\.git" -Recurse -Force
}
else {
    Write-Host "No nested .git directory found." -ForegroundColor Gray
}

# 2. Clear the git index for the target directory to remove any "gitlink"
Write-Host "Clearing git index for the target directory..." -ForegroundColor Yellow
Set-Location -Path $RepoRoot
git rm --cached -r $TargetDir --ignore-unmatch

# 3. Add the files to the root repository
Write-Host "Adding files to the main repository..." -ForegroundColor Yellow
git add "$TargetDir"

Write-Host "Done. Please check 'git status' to verify the changes." -ForegroundColor Green
