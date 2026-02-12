$WshShell = New-Object -comObject WScript.Shell
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $DesktopPath "Onboarding Assistant.lnk"
$Target = Join-Path $PSScriptRoot "..\run_applet.bat"

$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $Target
$Shortcut.Description = "Launch Local AI Campaign Assistant Applet"
$Shortcut.IconLocation = "shell32.dll,43" 
$Shortcut.Save()

Write-Host "Shortcut created at: $ShortcutPath"
