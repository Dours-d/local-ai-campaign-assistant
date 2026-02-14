import os
import re
import json

# Paths
MESSAGES_DIR = "data/trustee_messages"
CAMPAIGNS_FILE = "data/campaigns_remaining.json"

def main():
    print("Mapping BIDs to Message Files via Content Search...", flush=True)

    # 1. Load BIDs
    bids = []
    try:
        with open(CAMPAIGNS_FILE, 'r', encoding='utf-8') as f:
            campaigns = json.load(f)
            bids = [str(c.get('bid')) for c in campaigns if c.get('bid')]
    except Exception as e:
        print(f"Error loading campaigns: {e}")
        return

    print(f"Loaded {len(bids)} BIDs from {CAMPAIGNS_FILE}")

    # 2. Scan Message Files
    mapping = {} # BID -> [filenames]
    
    if os.path.exists(MESSAGES_DIR):
        for filename in os.listdir(MESSAGES_DIR):
            if not filename.endswith(".txt"): continue
            filepath = os.path.join(MESSAGES_DIR, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                for bid in bids:
                    # Search for BID as a word or part of a URL
                    if bid in content:
                        print(f"FOUND: BID {bid} in {filename}")
                        if bid not in mapping:
                            mapping[bid] = []
                        mapping[bid].append(filename)
            except Exception as e:
                print(f"Error reading {filename}: {e}")

    # 3. Output mapping for later use
    with open('data/bid_to_message_mapping.json', 'w', encoding='utf-8') as f:
        json.dump(mapping, f, indent=2)
    
    print(f"Mapping complete. Found {len(mapping)} BIDs across messages.")

if __name__ == "__main__":
    main()
