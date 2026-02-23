import json
import os

REGISTRY_PATH = 'vault/UNIFIED_REGISTRY.json'

def fix_akram():
    if not os.path.exists(REGISTRY_PATH):
        print("Registry not found.")
        return

    with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    count = 0
    for camp in data:
        # Match Akram by WhatsApp primarily
        wa = str(camp.get('whatsapp') or '')
        if '972597341113' in wa:
            print(f"Fixing Akram record: {camp.get('bid')} | Identity: {camp.get('identity_name')}")
            camp['ishmael_id'] = 'A'
            camp['status'] = 'live' # Ensure it's live so it doesn't get wiped
            count += 1
        
    if count > 0:
        with open(REGISTRY_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Fixed {count} Akram records.")
    else:
        print("Akram record not found by WhatsApp.")

if __name__ == "__main__":
    fix_akram()
