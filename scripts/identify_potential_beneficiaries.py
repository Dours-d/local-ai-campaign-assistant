
import os
import json
import re

DATA_DIR = "data"
EXPORTS_DIR = os.path.join(DATA_DIR, "exports")

def list_numbered_names():
    numbered_contacts = []
    
    # Check no_campaign list
    no_campaign_file = os.path.join(DATA_DIR, "whatsapp_no_campaign.txt")
    if os.path.exists(no_campaign_file):
        with open(no_campaign_file, 'r', encoding='utf-8') as f:
            for line in f:
                name = line.strip()
                if name and (re.match(r'^\+?[\d\-_]{5,}', name) or "Please" in name or "help" in name.lower()):
                    numbered_contacts.append(name)

    # Cross-reference with exports to find if they are active
    active_numbered = []
    if os.path.exists(EXPORTS_DIR):
        files = os.listdir(EXPORTS_DIR)
        for name in numbered_contacts:
            # Match name to file (handling underscores/spaces)
            sanitized = name.replace(" ", "_")
            matches = [f for f in files if sanitized in f]
            if matches:
                active_numbered.append({
                    "name": name,
                    "file": matches[0],
                    "status": "Potential"
                })

    return active_numbered

if __name__ == "__main__":
    contacts = list_numbered_names()
    print(f"Found {len(contacts)} potential beneficiaries with numbered/placeholder names:")
    for c in contacts[:10]:
        print(f"- {c['name']} (File: {c['file']})")
    
    with open(os.path.join(DATA_DIR, "potential_beneficiaries.json"), "w", encoding='utf-8') as f:
        json.dump(contacts, f, indent=2)
