import json
import os

REGISTRY_PATH = 'vault/UNIFIED_REGISTRY.json'

def scrub():
    if not os.path.exists(REGISTRY_PATH):
        print("Registry not found.")
        return

    with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    cleaned = []
    seen_bids = set()
    used_ishmael_ids = {}

    print(f"Initial record count: {len(data)}")

    for camp in data:
        # Determine BID
        bid = camp.get('bid') or (camp.get('bids')[0] if camp.get('bids') else None)
        whatsapp = camp.get('whatsapp')
        
        # 1. Skip absolute ghosts (no BID, no WhatsApp)
        if not bid and not whatsapp:
            print(f"Skipping absolute ghost: {camp.get('title')[:30]}")
            continue

        # 2. Handle duplicates
        unique_id = bid or whatsapp
        if unique_id in seen_bids:
            # Merge logic if needed, or just prioritize records with ishmael_id
            existing = next(c for c in cleaned if (c.get('bid') or c.get('whatsapp')) == unique_id)
            if not existing.get('ishmael_id') and camp.get('ishmael_id'):
                existing['ishmael_id'] = camp['ishmael_id']
            continue
        
        seen_bids.add(unique_id)
        
        # 3. Validation: Only the first record with a specific Ishmael ID wins
        iid = camp.get('ishmael_id')
        if iid:
            if iid in used_ishmael_ids:
                print(f"Collision: {iid} already used by {used_ishmael_ids[iid]}. Clearing from {unique_id}")
                camp['ishmael_id'] = None
            else:
                used_ishmael_ids[iid] = unique_id
        
        cleaned.append(camp)

    print(f"Cleaned record count: {len(cleaned)}")

    with open(REGISTRY_PATH, 'w', encoding='utf-8') as f:
        json.dump(cleaned, f, indent=4, ensure_ascii=False)
    print("Scrubbing complete.")

if __name__ == "__main__":
    scrub()
