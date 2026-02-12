import json
import os
import re

DATA_DIR = "data"
INPUT_FILE = os.path.join(DATA_DIR, "potential_growth_list_audited.json")
OUTPUT_FILE = os.path.join(DATA_DIR, "potential_growth_list_final.json")
BENEFICIARIES_FILE = os.path.join(DATA_DIR, "potential_beneficiaries.json")
REGISTRY_FILE = os.path.join(DATA_DIR, "campaign_registry.json")

def get_next_trustee_index():
    # Find the maximum index used across all relevant files
    max_idx = 0
    
    # Check current potential list
    files_to_check = [BENEFICIARIES_FILE, INPUT_FILE]
    for path in files_to_check:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    if isinstance(data, list):
                        for b in data:
                            name = b.get('name', '')
                            # Match Trustee 001 or Trustee-001 or Trustee_001
                            match = re.search(r'Trustee[\s\-_](\d+)', name)
                            if match:
                                max_idx = max(max_idx, int(match.group(1)))
                except: continue
                
    # Check Registry mappings
    if os.path.exists(REGISTRY_FILE):
        with open(REGISTRY_FILE, 'r', encoding='utf-8') as f:
            try:
                registry = json.load(f).get("mappings", {})
                for key, val in registry.items():
                    name = val.get('name', '')
                    match = re.search(r'Trustee[\s\-_](\d+)', name)
                    if match:
                        max_idx = max(max_idx, int(match.group(1)))
                    # Also check keys
                    match_key = re.search(r'Trustee[\s\-_](\d+)', key)
                    if match_key:
                        max_idx = max(max_idx, int(match_key.group(1)))
            except: pass
            
    return max_idx + 1

def assign_identities():
    if not os.path.exists(INPUT_FILE):
        print("Input file not found.")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        contacts = json.load(f)

    next_idx = get_next_trustee_index()
    processed = []

    for c in contacts:
        # Check if it's already numbered
        if "Trustee" in c['name']:
            # Normalize existing: Remove dashes/underscores from name
            c['name'] = re.sub(r'Trustee[\s\-_]', 'Trustee ', c['name'])
            processed.append(c)
            continue
            
        # Strictly verify prefix +972, +970, or +967 and REMOVE all formatting
        clean_id = re.sub(r'\D', '', c['id'])
        if not clean_id.startswith(('972', '970', '967')):
            print(f"Skipping {c['id']} - Doesn't match strict prefix requirements.")
            continue
            
        new_name = f"Trustee {next_idx:03d}"
        c['name'] = new_name
        c['id'] = clean_id # Update ID to pure numeric
        c['numbered_id'] = new_name
        processed.append(c)
        next_idx += 1

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(processed, f, indent=2)

    print(f"Identity Assignment Complete:")
    print(f" - Assigned {len(processed)} numbered identities.")
    print(f" - Output saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    assign_identities()
