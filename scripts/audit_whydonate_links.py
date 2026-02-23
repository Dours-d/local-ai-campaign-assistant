import json
import os
import re

REGISTRY_FILE = 'data/campaign_registry.json'
SUCCESS_FILE = 'data/success_campaigns.txt'

def audit():
    if not os.path.exists(REGISTRY_FILE):
        return
        
    with open(REGISTRY_FILE, 'r', encoding='utf-8') as f:
        registry = json.load(f)

    mappings = registry.get("mappings", {})
    fixed_count = 0
    
    for bid, data in mappings.items():
        url = data.get('whydonate_url')
        if not url: continue
        
        original_url = url
        
        # 1. Fix leading dash in slug
        # https://whydonate.com/fundraising/-slug -> help-slug
        if 'whydonate.com/fundraising/-' in url:
            url = url.replace('whydonate.com/fundraising/-', 'whydonate.com/fundraising/')
            
        # 2. Fix typos
        url = url.replace('elp-magda', 'help-magda')
        
        # 3. Ensure help prefix if it looks like it was intended
        # (This is risky, only if it starts with the bid-like number and no dashes)
        
        # 4. Global Dash Cleanup for Whydonate - remove any double slashes or accidental characters
        url = url.replace('fundraising//', 'fundraising/')
        
        if url != original_url:
            data['whydonate_url'] = url
            fixed_count += 1
            print(f"Fixed {bid}: {original_url} -> {url}")

    if fixed_count > 0:
        with open(REGISTRY_FILE, 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=2)
        print(f"Audit complete. Fixed {fixed_count} links in registry.")
    else:
        print("No registry WhyDonate links needed fixing.")

    # Also check success_campaigns.txt
    if os.path.exists(SUCCESS_FILE):
        with open(SUCCESS_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        new_lines = []
        for line in lines:
            if 'whydonate.com/fundraising/-' in line:
                line = line.replace('whydonate.com/fundraising/-', 'whydonate.com/fundraising/')
            new_lines.append(line)
            
        with open(SUCCESS_FILE, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)

if __name__ == "__main__":
    audit()
