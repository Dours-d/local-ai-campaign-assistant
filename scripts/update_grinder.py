
import json
import os
import re

BENEFICIARIES_FILE = "data/potential_beneficiaries.json"
SOURCE_FILE = "data/campaignless_whatsapp.txt"

def normalize(number):
    return "".join(re.findall(r'\d+', str(number)))

def add_to_grinder():
    if not os.path.exists(BENEFICIARIES_FILE):
        print("Error: potential_beneficiaries.json not found.")
        return
    if not os.path.exists(SOURCE_FILE):
        print("Error: campaignless_whatsapp.txt not found.")
        return

    # Load existing beneficiaries
    with open(BENEFICIARIES_FILE, 'r', encoding='utf-8') as f:
        beneficiaries = json.load(f)
    
    existing_ids = {normalize(b['name']) for b in beneficiaries}
    
    # Extract numbers from source file
    new_entries = []
    with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('+'):
                normalized = normalize(line)
                if normalized and normalized not in existing_ids:
                    # Construct name: keep + and spaces/dashes as stored in the source file
                    # but normalize for identifier consistency
                    name = line.split(' ')[0] + "_" + "-".join(re.findall(r'\d+', line.split(' ')[1])) if '-' in line else line.replace(" ", "_")
                    # Actually, the existing format seems to be 972_59-211-3473
                    # Let's try to match that format if possible, or just use the number string
                    
                    # More consistent: replace spaces with _ and - with -
                    formatted_name = line.replace(" ", "_")
                    if "_" in formatted_name:
                         # e.g. +972_59-746-5525
                         formatted_name = formatted_name.replace("+", "")
                    
                    beneficiaries.append({
                        "name": formatted_name,
                        "file": f"{formatted_name}.json",
                        "status": "Potential"
                    })
                    existing_ids.add(normalized)
                    new_entries.append(formatted_name)

    # Save updated list
    with open(BENEFICIARIES_FILE, 'w', encoding='utf-8') as f:
        json.dump(beneficiaries, f, indent=2)

    print(f"Added {len(new_entries)} new contacts to {BENEFICIARIES_FILE}")

if __name__ == "__main__":
    add_to_grinder()
