
import json
import os
import re

def normalize_text(text):
    if not text: return ""
    return re.sub(r'\s+', ' ', text).strip()

def prepare_launchgood_data():
    unified_path = 'data/campaigns_unified.json'
    if not os.path.exists(unified_path):
        print("Unified database not found.")
        return

    with open(unified_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    launchgood_batch = []
    
    # We want campaigns that are not already on Whydonate or Chuffed? 
    # Actually, the user says "duplicate the Whole lot".
    # I'll focus on the ones marked as 'pending_migration' in our previous context
    # or just take the first 50 from the unified database for now.
    
    for c in data.get('campaigns', []):
        # Skip if already has a whydonate URL? 
        # No, user wants to duplicate to LaunchGood specifically.
        
        raw_title = c.get('title', '')
        title = raw_title[:100] # LaunchGood limit
        
        # Tagline: 160 chars. We can use the first sentence or part of title.
        tagline = raw_title[:160]
        
        # Story: LaunchGood needs a pitch. 
        # We'll use the title as a placeholder for now, or a generic template.
        story = f"<h2>{raw_title}</h2>\n<p>Please help us support this cause in Gaza. We are the natural owners of our time and resources, and we allocate them here to preserve life and dignity.</p>\n<p>Beneficiary ID: {c.get('privacy', {}).get('internal_name', 'Verifying...')}</p>"
        
        item = {
            "id": c.get('id'),
            "title": title,
            "tagline": tagline,
            "story": story,
            "goal": 5000, # Default goal
            "currency": "EUR",
            "image": c.get('image_url'),
            "internal_name": c.get('privacy', {}).get('internal_name'),
            "source_url": c.get('url'),
            "status": "pending_launchgood"
        }
        launchgood_batch.append(item)

    output_path = 'data/launchgood_batch_create.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(launchgood_batch, f, indent=2)
    
    print(f"Prepared {len(launchgood_batch)} campaigns for LaunchGood.")

if __name__ == "__main__":
    prepare_launchgood_data()
