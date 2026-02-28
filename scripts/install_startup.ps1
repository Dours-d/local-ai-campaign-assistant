$WshShell = New-Object -comObject WScript.Shell
$StartupPath = [Environment]::GetFolderPath("Startup")
$ShortcutPath = Join-Path $StartupPath "Sovereign_HeadQuarters.lnk"
$Target = Join-Path $PSScriptRoot "..\Start_HeadQuarters.bat"

$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $Target
$Shortcut.WorkingDirectory = Join-Path $PSScriptRoot ".."
$Shortcut.Description = "Launch Sovereign HeadQuarters & Watchdog on Boot"
$Shortcut.IconLocation = "shell32.dll,43" 
$Shortcut.Save()

Write-Host "Startup shortcut created at: $ShortcutPath"
