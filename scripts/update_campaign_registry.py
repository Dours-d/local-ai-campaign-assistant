import json
import os
import glob
from datetime import datetime

ONBOARDING_DIR = "data/onboarding_submissions"
REGISTRY_FILE = "data/campaign_registry.json"
UNIFIED_DB = "data/campaigns_unified.json"
VAULT_MAPPING = "data/vault_mapping.json"
LAUNCHGOOD_DEFAULT = "https://bit.ly/g-gz-resi-fund"

def load_json(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def main():
    registry = load_json(REGISTRY_FILE)
    if "mappings" not in registry:
        registry["mappings"] = {}
        
    vault = load_json(VAULT_MAPPING)
    
    # 1. Process Onboarding Submissions
    submission_files = glob.glob(os.path.join(ONBOARDING_DIR, "*.json"))
    for file_path in submission_files:
        sub = load_json(file_path)
        bid = sub.get("beneficiary_id")
        if not bid: continue
        
        if bid not in registry["mappings"]:
            registry["mappings"][bid] = {
                "name": sub.get("display_name") or sub.get("title", "")[:50],
                "whatsapp": sub.get("whatsapp_number"),
                "launchgood_url": LAUNCHGOOD_DEFAULT,
                "whydonate_url": None,
                "wallet_address": None,
                "onboarding_status": "submitted",
                "last_updated": datetime.now().isoformat()
            }
            
    # 2. Update Wallets from Vault Mapping
    for bid, data in registry["mappings"].items():
        phone = data.get("whatsapp")
        if phone:
            # Try to match phone in vault (handling different formats)
            clean_phone = "".join(filter(str.isdigit, phone))
            for v_key, v_data in vault.items():
                v_clean = "".join(filter(str.isdigit, v_key))
                if clean_phone and v_clean and clean_phone in v_clean:
                    data["wallet_address"] = v_data.get("address")
                    break

    # 3. Save
    registry["stats"] = {
        "total_beneficiaries": len(registry["mappings"]),
        "last_sync": datetime.now().isoformat()
    }
    save_json(REGISTRY_FILE, registry)
    print(f"Registry updated: {len(registry['mappings'])} entries.")

if __name__ == "__main__":
    main()
