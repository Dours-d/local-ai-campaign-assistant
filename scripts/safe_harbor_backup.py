
import os
import shutil
import zipfile
from datetime import datetime

# Define what constitutes "Sensible Data"
SENSIBLE_FILES = [
    ".env",
    "data/internal_ledger.json",
    "data/vault_mapping.json",
    "data/payouts_completed.json",
    "data/campaign_coupling.json"
]

SENSIBLE_DIRS = [
    "data/onboarding_submissions",
    "data/reports"
]

BACKUP_ROOT = "backups/safe_harbor"

def create_backup():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_folder = os.path.join(BACKUP_ROOT, f"backup_{timestamp}")
    os.makedirs(backup_folder, exist_ok=True)
    
    print(f"--- Starting 'Safe Harbor' Backup: {timestamp} ---")
    
    # 1. Copy Files
    for file_path in SENSIBLE_FILES:
        if os.path.exists(file_path):
            dest = os.path.join(backup_folder, os.path.basename(file_path))
            shutil.copy2(file_path, dest)
            print(f"Saved file: {file_path}")
        else:
            print(f"Warning: File not found: {file_path}")

    # 2. Copy Directories
    for dir_path in SENSIBLE_DIRS:
        if os.path.exists(dir_path):
            dest = os.path.join(backup_folder, os.path.basename(dir_path))
            shutil.copytree(dir_path, dest, dirs_exist_ok=True)
            print(f"Saved directory: {dir_path}")
        else:
            print(f"Warning: Directory not found: {dir_path}")

    # 3. Create Zip Archive for easy transfer to airgapped device
    zip_path = f"{backup_folder}.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(backup_folder):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, backup_folder)
                zipf.write(abs_path, rel_path)

    print(f"--- Backup Complete ---")
    print(f"Archive ready for airgap: {zip_path}")
    
    # Cleanup the temporary folder (keep the zip)
    shutil.rmtree(backup_folder)

if __name__ == "__main__":
    create_backup()
