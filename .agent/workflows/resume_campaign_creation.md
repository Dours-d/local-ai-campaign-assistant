---
description: Resume WhyDonate campaign creation from the current batch queue.
---

This workflow outlines how to resume the automated creation of campaigns on WhyDonate using the existing batch queue.

### 1. Preparation
- Ensure the `batch_queue.json` file in `data/` contains the campaigns you want to create.
- Ensure you have a browser instance running in debug mode.

// turbo
### 2. Launch Debug Browser
Run the following command to open Edge for automation:
```powershell
./debug_edge.bat
```
- **Login**: Manually log in to WhyDonate if not already authenticated.
- **Navigate**: Go to the "Start Fundraiser" page or stay on the dashboard.

### 3. Run the Automater
// turbo
Execute the batch automater script:
```powershell
python scripts/whydonate_batch_automater.py
```
- The script will process campaigns in `data/batch_queue.json`.
- It handles Step 1 (Title/Category/Location), Step 2 (Beneficiary is "YOURSELF"), Step 3 (Title/Story/Image), and Step 4 (Goal/Finalization).

### 4. Monitor Progress
- Check `automater_log.txt` for real-time output and error details.
- Verify each created campaign against the `MANUAL_CAMPAIGN_LEDGER.md`.

### 5. Finalization
- After a successful run, update the WhyDonate URLs in `MANUAL_CAMPAIGN_LEDGER.md`.
- Run `python scripts/implement_name_policy.py` to ensure local registries are in sync if necessary.
- If a campaign fails, the script is designed to skip it and proceed to the next after a timeout.