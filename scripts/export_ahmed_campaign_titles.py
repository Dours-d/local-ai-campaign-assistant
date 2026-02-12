import json
import os
import csv

LEDGER_FILE = 'data/isolated/ahmed/ahmed_ledger.json'
CAMPAIGNS_UNIFIED = 'data/campaigns_unified.json'
OUTPUT_DIR = 'data/isolated/ahmed/campaign_lists'

def export_campaign_titles():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # 1. Load Ahmed Ledger
    with open(LEDGER_FILE, 'r', encoding='utf-8') as f:
        ahmed_ledger = json.load(f)

    # 2. Load Unified Campaigns
    with open(CAMPAIGNS_UNIFIED, 'r', encoding='utf-8') as f:
        unified_data = json.load(f)
        campaigns = unified_data.get('campaigns', [])

    # Create a map of ID -> Title
    id_to_title = {c['id']: c.get('title', 'No Title') for c in campaigns}

    # 3. Process each Ahmed
    for ahmed_id, data in ahmed_ledger.items():
        campaign_ids = data.get('campaigns', [])
        rows = []
        for cid in campaign_ids:
            title = id_to_title.get(cid, 'Title not found in unified index')
            rows.append({"Campaign ID": cid, "Title": title})

        # Save to separate CSV
        safe_name = ahmed_id.replace('-', '_')
        csv_path = os.path.join(OUTPUT_DIR, f"{safe_name}_campaigns.csv")
        
        with open(csv_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["Campaign ID", "Title"])
            writer.writeheader()
            writer.writerows(rows)
            
    print(f"Exported campaign lists for {len(ahmed_ledger)} Ahmeds to {OUTPUT_DIR}")

if __name__ == "__main__":
    export_campaign_titles()
