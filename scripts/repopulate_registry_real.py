import json
import os
import re

ACTIVE_ROOT = os.environ.get('ACTIVE_ROOT', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REGISTRY_PATH = os.path.join(ACTIVE_ROOT, 'data', 'UNIFIED_REGISTRY.json')
BATCH_QUEUE_PATH = os.path.join(ACTIVE_ROOT, 'data', 'batch_queue.json')
CAMPAIGN_INDEX_PATH = os.path.join(ACTIVE_ROOT, 'data', 'campaign_index.json')
WD_LIST_PATH = os.path.join(ACTIVE_ROOT, 'data', 'whydonate_campaigns_list.csv')

def load_csv_urls():
    """Load Whydonate URLs from the CSV list."""
    url_map = {}
    if not os.path.exists(WD_LIST_PATH):
        return url_map
    
    with open(WD_LIST_PATH, 'r', encoding='utf-8') as f:
        # Simple CSV parsing
        lines = f.readlines()
        for line in lines[1:]: # Skip header
            parts = line.strip().split('","')
            if len(parts) >= 3:
                wd_id = parts[0].replace('"', '')
                title = parts[2].replace('"', '')
                # Reconstruct URL from ID: whydonate_help-mohamad... -> whydonate.com/fundraising/help-mohamad...
                clean_slug = wd_id.replace('whydonate_', '')
                url_map[title] = f"https://whydonate.com/fundraising/{clean_slug}"
    return url_map

def generate_wd_slug(title):
    """Generate a valid Whydonate slug from a title."""
    # 1. Lowercase
    slug = title.lower()
    # 2. Replace non-alphanumeric with hyphens
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    # 3. Collapse multiple hyphens
    slug = re.sub(r'-+', '-', slug)
    # 4. Trim hyphens from ends
    return slug.strip('-')

def repopulate():
    print("🔄 Starting Mass Materialization (Link Integrity Fix)...")
    
    # 1. Load data
    with open(BATCH_QUEUE_PATH, 'r', encoding='utf-8') as f:
        batch_queue = json.load(f)
    
    with open(CAMPAIGN_INDEX_PATH, 'r', encoding='utf-8') as f:
        campaign_index = json.load(f)
        
    # We still use wd_list to only include campaigns that actually exist in our scraped list
    # but we will derive the URL correctly.
    url_map = {}
    if os.path.exists(WD_LIST_PATH):
        with open(WD_LIST_PATH, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines[1:]:
                parts = line.strip().split('","')
                if len(parts) >= 3:
                    full_title = parts[2].replace('"', '')
                    url_map[full_title] = f"https://whydonate.com/fundraising/{generate_wd_slug(full_title)}"

    new_registry = []
    
    # 2. Process first 50 entries
    count = 0
    for entry in batch_queue:
        if count >= 50:
            break
            
        bid = entry.get('bid')
        title = entry.get('title')
        
        # Try to find a live URL
        whydonate_url = ""
        
        # Check by title first using our generated slug logic
        if title in url_map:
            whydonate_url = url_map[title]

        # If no URL found, skip to keep production clean
        if not whydonate_url:
            continue

        # Clean the title
        clean_title = title.split('|')[0].strip()
        
        # Map to registry format
        new_entry = {
            "whatsapp": bid,
            "norm_whatsapp": re.sub(r'\D', '', bid),
            "title": clean_title,
            "custom_identity_name": clean_title,
            "description": entry.get('description', '').split('---')[-1].strip(), # Get English part
            "goal": entry.get('goal', 10000),
            "status": "live",
            "bids": [bid],
            "image": entry.get('image', '').replace(ACTIVE_ROOT + os.sep, '').replace('\\', '/'),
            "whydonate_url": whydonate_url,
            "ishmael_id": f"R{count+1:03d}", # R for Real
            "story": entry.get('story', "We are the natural owners of our time and our solidarity. Join us in preserving life and dignity.")
        }
        
        new_registry.append(new_entry)
        count += 1

    # 3. Save to registry
    with open(REGISTRY_PATH, 'w', encoding='utf-8') as f:
        json.dump(new_registry, f, indent=4, ensure_ascii=False)
        
    print(f"✅ Materialized {len(new_registry)} real families with fixed production links.")

if __name__ == "__main__":
    repopulate()
