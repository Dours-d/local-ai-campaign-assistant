import json
import os

SOURCE = "data/rationalized_growth_list.json"
TARGET = "data/potential_beneficiaries.json"

def merge():
    if not os.path.exists(SOURCE):
        print(f"Source {SOURCE} not found.")
        return
    
    with open(SOURCE, "r", encoding="utf-8") as f:
        growth_list = json.load(f)
    
    if os.path.exists(TARGET):
        with open(TARGET, "r", encoding="utf-8") as f:
            beneficiaries = json.load(f)
    else:
        beneficiaries = []
    
    existing_ids = {b['id'] for b in beneficiaries}
    added_count = 0
    
    for entry in growth_list:
        bid = entry['id']
        if bid not in existing_ids:
            # Convert growth list format to beneficiary format
            new_entry = {
                "name": entry['name'],
                "id": bid,
                "status": "Expansion Batch"
            }
            beneficiaries.append(new_entry)
            existing_ids.add(bid)
            added_count += 1
            
    with open(TARGET, "w", encoding="utf-8") as f:
        json.dump(beneficiaries, f, indent=2)
    
    print(f"Merge Complete: Added {added_count} new contacts. Total: {len(beneficiaries)}")

if __name__ == "__main__":
    merge()
