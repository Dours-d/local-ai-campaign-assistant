
import json
import os
import re

DATA_DIR = "data"
BENEFICIARIES_FILE = os.path.join(DATA_DIR, "potential_beneficiaries.json")
ONBOARDING_LIST_V2 = os.path.join(DATA_DIR, "new_whatsapp_onboarding_list_v2.json")
UNIFIED_FILE = os.path.join(DATA_DIR, "campaigns_unified.json")
REGISTRY_FILE = os.path.join(DATA_DIR, "campaign_registry.json")
OUTBOX_DIR = os.path.join(DATA_DIR, "onboarding_outbox")

def normalize(name):
    if not name: return ""
    return str(name).strip('_').strip().lower()

def is_rational(bid):
    clean_id = re.sub(r'\D', '', str(bid))
    bid_str = str(bid).lower()
    
    # Noise/Message keywords
    if any(k in bid_str for k in ['please', 'help', 'brother', 'answer', 'children', 'money', 'ignoring']):
        return False
    
    # Regional filter (+972, +970, +967)
    if not clean_id.startswith(('972', '970', '967')):
        return False
        
    if len(clean_id) < 9 or len(clean_id) > 15:
        return False
        
    return True

def get_exclusion_set():
    exclusions = set()
    
    # 1. Existing Campaigns
    if os.path.exists(UNIFIED_FILE):
        with open(UNIFIED_FILE, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                entries = data.items() if isinstance(data, dict) else [(None, e) for e in data]
                for _, e in entries:
                    bid = e.get('beneficiary_id') or e.get('id')
                    if bid: exclusions.add(normalize(bid))
                    iname = e.get('internal_name')
                    if iname: exclusions.add(normalize(iname))
            except: pass
            
    # 2. Registry (Wallets)
    if os.path.exists(REGISTRY_FILE):
        with open(REGISTRY_FILE, 'r', encoding='utf-8') as f:
            try:
                reg = json.load(f).get("mappings", {})
                for k in reg: exclusions.add(normalize(k))
            except: pass
            
    return exclusions

def cleanup_file(path, key_name='id'):
    if not os.path.exists(path): return
    
    exclusions = get_exclusion_set()
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    clean_data = []
    removed_count = 0
    
    for item in data:
        val = item.get(key_name) or item.get('name')
        if not val: continue
        
        norm_val = normalize(val)
        clean_digits = re.sub(r'\D', '', norm_val)
        
        # 1. Rationality Check
        if not is_rational(val):
            print(f"Removing Noise: {val}")
            removed_count += 1
            continue
            
        # 2. Redundancy Check
        if norm_val in exclusions or clean_digits in exclusions:
            print(f"Removing Redundant: {val}")
            removed_count += 1
            continue
            
        clean_data.append(item)
        
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(clean_data, f, indent=2)
    
    print(f"Cleaned {path}: Removed {removed_count} items. Remaining: {len(clean_data)}")

def cleanup_outbox():
    if not os.path.exists(OUTBOX_DIR): return
    
    exclusions = get_exclusion_set()
    # Also get currently valid potential beneficiaries
    potential_ids = set()
    if os.path.exists(BENEFICIARIES_FILE):
        with open(BENEFICIARIES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for item in data:
                val = item.get('id') or item.get('name')
                if val: potential_ids.add(normalize(val))

    removed_count = 0
    for f in os.listdir(OUTBOX_DIR):
        # Extract the base ID from the filename
        # Pattern: ID_onboarding.txt or ID_campaign_PENDING.txt
        base_id = normalize(f.replace('_onboarding.txt', '').replace('_campaign_PENDING.txt', ''))
        
        # If it's a "Trustee XXX" file, check it differently
        if base_id.startswith('trustee'):
             # We should probably keep these if they are in the growth list
             continue

        # If it's noise or already redundant (onboarded), remove it
        clean_digits = re.sub(r'\D', '', base_id)
        
        if not is_rational(base_id) or base_id in exclusions or clean_digits in exclusions:
            if base_id not in potential_ids:
                print(f"Removing Outbox File: {f}")
                try:
                    os.remove(os.path.join(OUTBOX_DIR, f))
                    removed_count += 1
                except: pass
                
    print(f"Cleaned Outbox: Removed {removed_count} noise/redundant files.")

if __name__ == "__main__":
    cleanup_file(BENEFICIARIES_FILE, 'name')
    cleanup_file(ONBOARDING_LIST_V2, 'name')
    cleanup_outbox()
