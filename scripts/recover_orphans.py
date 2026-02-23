import json
import csv
import os
import re

def normalize(phone):
    if not phone: return ""
    return re.sub(r'\D', '', str(phone))

def recover_neglected_data():
    # Load orphans from previous audit logic (duplicated here for completeness)
    with open('campaign_index_full.json', 'r', encoding='utf-8') as f:
        registry = json.load(f)
    registry_normalized = {normalize(k): k for k in registry.keys()}
    
    with open('onboarding_messages.txt', 'r', encoding='utf-8') as f:
        messages_content = f.read()
    messages = re.split(r'-{30,}', messages_content)
    
    orphans = []
    for block in messages:
        if not block.strip(): continue
        id_match = re.search(r'MESSAGE FOR ([a-zA-Z0-9_+:-]+)', block)
        if not id_match:
            lines = block.strip().split('\n')
            if lines and re.match(r'^[a-zA-Z0-9_+:-]+$', lines[0]):
                bid = lines[0]
            else: continue
        else: bid = id_match.group(1)
        if normalize(bid) not in registry_normalized:
            orphans.append(bid)
    
    orphans = sorted(list(set(orphans)))
    print(f"Recovering data for {len(orphans)} orphans...")
    
    recovered_data = {}
    
    # Search in submissions_summary.csv
    if os.path.exists('submissions_summary.csv'):
        with open('submissions_summary.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                bid = row.get('beneficiary_id')
                wa = row.get('whatsapp_number')
                for orphan in orphans:
                    if bid == orphan or normalize(wa) == normalize(orphan):
                        if orphan not in recovered_data:
                            recovered_data[orphan] = {"whatsapp": wa, "id": bid, "source": "submissions_summary.csv"}

    # Search in campaign_beneficiaries.csv
    if os.path.exists('data/campaign_beneficiaries.csv'):
        with open('data/campaign_beneficiaries.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Common headers in our system
                phone = row.get('phone') or row.get('whatsapp') or row.get('number')
                bid = row.get('id') or row.get('beneficiary_id')
                for orphan in orphans:
                    if (phone and normalize(phone) == normalize(orphan)) or (bid and bid == orphan):
                        if orphan not in recovered_data:
                            recovered_data[orphan] = {"whatsapp": phone, "id": bid, "source": "campaign_beneficiaries.csv"}

    print(f"\nRecovered {len(recovered_data)} / {len(orphans)} orphans.")
    
    # Missing completely
    missing = [o for o in orphans if o not in recovered_data]
    if missing:
        print("\nCOMPLETELY GHOSTED (No data found anywhere):")
        for m in missing:
            print(f"  - {m}")
            
    # Save a repair file
    with open('data/orphan_recovery.json', 'w', encoding='utf-8') as f:
        json.dump(recovered_data, f, indent=2)
    print("\nSaved recovery data to data/orphan_recovery.json")

if __name__ == "__main__":
    recover_neglected_data()
