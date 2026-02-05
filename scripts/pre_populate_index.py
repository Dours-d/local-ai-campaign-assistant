import json
import csv
import os

INDEX_FILE = "data/campaign_index.json"
CHUFFED_CSV = "data/coupling_vetting.csv"
WHYDONATE_CSV = "data/whydonate_coupling_vetting.csv"

def format_whatsapp(num):
    if not num: return None
    num = "".join([c for c in str(num) if c.isdigit()])
    if not num: return None
    if not num.startswith("+"):
        num = "+" + num
    return num

def pre_populate():
    index = {}

    # 1. Process Chuffed CSV
    if os.path.exists(CHUFFED_CSV):
        with open(CHUFFED_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                whatsapp = format_whatsapp(row.get('number'))
                chuffed_id = row.get('chuffed_id')
                if whatsapp and chuffed_id:
                    if whatsapp not in index: index[whatsapp] = {}
                    # We store the ID for now, can be used to reconstruct URL
                    index[whatsapp]['chuffed'] = {
                        "id": chuffed_id,
                        "url": f"https://chuffed.org/project/{chuffed_id}"
                    }

    # 2. Process Whydonate CSV
    if os.path.exists(WHYDONATE_CSV):
        with open(WHYDONATE_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                whatsapp = format_whatsapp(row.get('number'))
                title = row.get('whydonate_title')
                if whatsapp and title:
                    if whatsapp not in index: index[whatsapp] = {}
                    # Whydonate doesn't have an ID in this CSV, but we have the title
                    if 'whydonate' not in index[whatsapp]:
                        index[whatsapp]['whydonate'] = {
                            "title": title
                        }

    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2)
    
    print(f"Pre-populated index with {len(index)} WhatsApp entries.")

if __name__ == "__main__":
    pre_populate()
