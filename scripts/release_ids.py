import json
import os

REGISTRY_PATH = 'vault/UNIFIED_REGISTRY.json'

def release_ids():
    if not os.path.exists(REGISTRY_PATH):
        print("Registry not found.")
        return

    with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    count = 0
    for camp in data:
        iid = camp.get('ishmael_id')
        if iid in ['A', 'B']:
            print(f"Releasing {iid} from {camp.get('bid') or camp.get('bids', [None])[0] or camp.get('whatsapp')} ({camp.get('title')[:30]})")
            camp['ishmael_id'] = None
            count += 1
        
        # Also ensure Akram records have identity 'Akram' if they look like Akram
        if 'Akram' in str(camp.get('title')) or 'Akram' in str(camp.get('registry_name')):
             # Just to be sure we are working with the right record
             pass

    with open(REGISTRY_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"Surgical release complete. {count} records updated.")

if __name__ == "__main__":
    release_ids()
