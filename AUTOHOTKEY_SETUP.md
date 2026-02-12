# AutoHotkey Installation & Setup

## Prerequisites
AutoHotkey must be installed on your system. Download from: https://www.autohotkey.com/

## Quick Start
1. **Install AutoHotkey** (if not already installed)
   - Download from https://www.autohotkey.com/
   - Run the installer
   - Choose "Current User" installation

2. **Run the Onboarding Assistant**
   - Double-click `onboarding_assistant.ahk`
   - A green "H" icon will appear in your system tray

3. **Use the Tool**
   - Select a phone number (e.g., `972595561188`)
   - Press `Ctrl+Alt+O`
   - A tooltip will say "Message copied!"
   - Press `Ctrl+V` to paste the message

4. **Stop the Tool**
   - Press `Ctrl+Alt+Q` to exit
   - OR right-click the green "H" icon → Exit

## Features
- ✅ Native Windows hotkey handling (no timing issues)
- ✅ Automatic 12-digit phone number limiting
- ✅ Visual tooltip feedback
- ✅ No Python dependencies
- ✅ Lightweight and fast

## Troubleshooting
**Q: Script won't run**
- Make sure AutoHotkey is installed
- Right-click script → "Run as administrator"

**Q: Hotkey doesn't work**
- Check if another program is using `Ctrl+Alt+O`
- Try closing other running `.ahk` scripts

**Q: Wrong text copied**
- Make sure only the phone number is selected
- The script limits to 12 digits automatically
