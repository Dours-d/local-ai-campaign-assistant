$WshShell = New-Object -comObject WScript.Shell
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $DesktopPath "Campaign Management Corridor.lnk"
$Target = Join-Path $PSScriptRoot "..\Start_HeadQuarters.bat"

$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $Target
$Shortcut.WorkingDirectory = Join-Path $PSScriptRoot ".."
$Shortcut.Description = "Launch Sovereign HeadQuarters & Watchdog"
$Shortcut.IconLocation = "shell32.dll,43" 
$Shortcut.Save()

Write-Host "Desktop shortcut created at: $ShortcutPath"
