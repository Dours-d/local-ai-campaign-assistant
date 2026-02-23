import re
import json
import csv
import os

def normalize(phone):
    if not phone: return ""
    # Remove all non-digit characters
    return re.sub(r'\D', '', str(phone))

def identify_orphans_normalized():
    if not os.path.exists('campaign_index_full.json'):
        print("Registry missing.")
        return

    with open('campaign_index_full.json', 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    registry_normalized = {}
    for phone, entry in registry.items():
        norm_phone = normalize(phone)
        registry_normalized[norm_phone] = entry
        if entry.get('beneficiary_id'):
            registry_normalized[normalize(entry['beneficiary_id'])] = entry
            
    with open('onboarding_messages.txt', 'r', encoding='utf-8') as f:
        messages_content = f.read()
    
    messages = re.split(r'-{30,}', messages_content)
    
    orphans = []
    found_count = 0
    for block in messages:
        if not block.strip(): continue
        id_match = re.search(r'MESSAGE FOR ([a-zA-Z0-9_+:-]+)', block)
        if not id_match:
            lines = block.strip().split('\n')
            if lines and re.match(r'^[a-zA-Z0-9_+:-]+$', lines[0]):
                beneficiary_id = lines[0]
            else: continue
        else:
            beneficiary_id = id_match.group(1)
            
        norm_id = normalize(beneficiary_id)
        if norm_id in registry_normalized:
            found_count += 1
        else:
            orphans.append(beneficiary_id)
            
    print(f"Audit Results (Normalized):")
    print(f"  - Total Messages: {len(messages)}")
    print(f"  - Found in Registry: {found_count}")
    print(f"  - True Orphans: {len(orphans)}")
    
    if orphans:
        print("\nTRUE ORPHANS (Not in Registry even with normalization):")
        for o in sorted(list(set(orphans))):
            print(f"  - {o}")

if __name__ == "__main__":
    identify_orphans_normalized()
