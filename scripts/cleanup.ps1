# Workspace Cleanup Script
# This script moves old logs and debug files to an archive folder.

$WorkDir = Get-Location
$ArchiveDir = "$WorkDir\data\archive"

if (-not (Test-Path $ArchiveDir)) {
    New-Item -ItemType Directory -Path $ArchiveDir -Force
}

$FilesToArchive = @(
    "debug_output.txt",
    "debug_output_2.txt",
    "debug_output_3.txt",
    "debug_output_4.txt",
    "debug_output_5.txt",
    "debug_output_6.txt",
    "diag_output.txt",
    "run_output.log",
    "run_output_v2.log",
    "whydonate_dashboard_debug.html",
    "whydonate_debug.html",
    "debug_html_dump.txt"
)

foreach ($File in $FilesToArchive) {
    if (Test-Path "$WorkDir\$File") {
        Write-Host "Archiving $File..." -ForegroundColor Cyan
        Move-Item -Path "$WorkDir\$File" -Destination "$ArchiveDir\$File" -Force
    }
}

Write-Host "Workspace cleaned up! Legacy logs moved to data/archive." -ForegroundColor Green
