import json
import os

UNIFIED_PATH = 'data/campaigns_unified.json'
LEDGER_PATH = 'data/internal_ledger.json'

def sync_ledger_names():
    with open(UNIFIED_PATH, 'r', encoding='utf-8') as f:
        unified = json.load(f)
    with open(LEDGER_PATH, 'r', encoding='utf-8') as f:
        ledger = json.load(f)

    # Map of ID -> Internal Name
    id_to_name = {c['id']: c['privacy'].get('internal_name') for c in unified.get('campaigns', []) if c['privacy'].get('internal_name')}

    new_ledger = {}
    
    # Process the ledger
    # Note: Ledger entries often have a 'campaigns' list.
    # We should identify which name in unified corresponds to which ledger key.
    
    # Simple strategy: for each ledger key, see if its campaigns mapped to a new name
    for old_name, data in ledger.items():
        campaigns = data.get('campaigns', [])
        found_new_name = None
        for cid in campaigns:
            if cid in id_to_name:
                found_new_name = id_to_name[cid]
                break
        
        target_name = found_new_name if found_new_name else old_name
        
        if target_name in new_ledger:
            # Merge data if needed (homonym collision logic)
            # For now, just print warning if collision occurs unexpectedly
            print(f"Warning: collision detected for {target_name}. Merging.")
            for k, v in data.items():
                if isinstance(v, float) or isinstance(v, int):
                    new_ledger[target_name][k] = new_ledger[target_name].get(k, 0) + v
                elif isinstance(v, list):
                    new_ledger[target_name][k] = list(set(new_ledger[target_name].get(k, []) + v))
        else:
            new_ledger[target_name] = data

    with open(LEDGER_PATH, 'w', encoding='utf-8') as f:
        json.dump(new_ledger, f, indent=4)
        
    print("Ledger names synced with unified database.")

if __name__ == "__main__":
    sync_ledger_names()
