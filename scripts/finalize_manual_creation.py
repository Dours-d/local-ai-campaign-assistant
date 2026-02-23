import json
import re
import os
import subprocess

REGISTRY_FILE = "data/campaign_registry.json"
BATCH_QUEUE_FILE = "data/batch_queue.json"

def slugify(text):
    # Extract English part before the pipe if present
    if "|" in text:
        text = text.split("|")[0]
    
    text = text.lower()
    # Remove non-alphanumeric chars (keep spaces and hyphens)
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    # Replace spaces with hyphens
    text = re.sub(r'\s+', '-', text)
    # Remove leading/trailing hyphens
    return text.strip('-')

def update_registry_and_generate():
    with open(BATCH_QUEUE_FILE, 'r', encoding='utf-8') as f:
        queue = json.load(f)
    
    with open(REGISTRY_FILE, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    mappings = registry.get("mappings", {})
    
    updated_count = 0
    for item in queue:
        bid = item['bid']
        title = item['title']
        
        # Construct expected URL
        slug = slugify(title)
        url = f"https://whydonate.com/fundraising/{slug}"
        
        if bid in mappings:
            print(f"Updating {bid} -> {url}")
            mappings[bid]['whydonate_url'] = url
            mappings[bid]['onboarding_status'] = 'published' # User said they created them
            updated_count += 1
        else:
            print(f"Warning: BID {bid} not found in registry mappings, creating entry.")
            mappings[bid] = {
                "name": item.get('display_name', 'Beneficiary'), # Fallback
                "whatsapp": "", # Needs to be filled if possible, but taking from ID if valid
                "whydonate_url": url,
                "onboarding_status": "published"
            }
            # Try to infer whatsapp from BID if it looks like one
            if bid.startswith("972") or bid.startswith("059"):
                 mappings[bid]["whatsapp"] = "+" + bid if not bid.startswith("+") else bid

    registry['mappings'] = mappings
    
    with open(REGISTRY_FILE, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2)
    
    print(f"Updated {updated_count} campaigns in registry.")
    
    # Now generate the messages
    print("Generating onboarding messages...")
    subprocess.run(["python", "scripts/generate_onboarding_messages.py"], check=True)

if __name__ == "__main__":
    update_registry_and_generate()
