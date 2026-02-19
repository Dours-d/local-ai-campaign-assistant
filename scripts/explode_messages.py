import os
import re
import json

MESSAGES_FILE = 'onboarding_messages.txt'
REGISTRY_FILE = 'campaign_index_full.json'
OUTBOX_DIR = 'data/onboarding_outbox'

def explode_messages():
    if not os.path.exists(OUTBOX_DIR):
        os.makedirs(OUTBOX_DIR)
    
    # Load registry for better naming
    try:
        with open(REGISTRY_FILE, 'r', encoding='utf-8') as f:
            registry = json.load(f)
    except Exception:
        registry = {}

    with open(MESSAGES_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by the header pattern
    # --- MESSAGE FOR {ID} ---
    blocks = re.split(r'--- MESSAGE FOR (\d+) ---', content)
    
    # The first element is usually empty or preamble
    # Then we have pairs of (ID, MessageContent)
    
    count = 0
    for i in range(1, len(blocks), 2):
        bid = blocks[i]
        message = blocks[i+1].strip()
        
        # Determine name from registry
        name = "Unknown"
        if bid in registry:
            # Check for whydonate title or other name indicator
            wd = registry[bid].get('whydonate', {})
            name = wd.get('title', 'Beneficiary').split(' | ')[-1] # Try to get the specific name
            name = re.sub(r'[^\w\s]', '', name).replace(' ', '_')
        
        filename = f"{bid}_{name}.txt"
        filepath = os.path.join(OUTBOX_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as out:
            out.write(f"--- OFFICIAL MISSION MESSAGE FOR {bid} ---\n\n")
            out.write(message)
        
        count += 1
        print(f"Created: {filename}")

    print(f"\nTotal missions exploded into truths: {count}")

if __name__ == "__main__":
    explode_messages()
