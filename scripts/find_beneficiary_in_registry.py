import json
import os

def main():
    print("Searching campaign_registry.json...", flush=True)
    try:
        with open('data/campaign_registry.json', 'r', encoding='utf-8') as f:
            reg = json.load(f)
        
        mappings = reg.get('mappings', {})
        found = False
        for key, val in mappings.items():
            name = val.get('name', '')
            if not name: continue
            if 'Aya' in name or 'Mohammed' in name:
                print(f"FOUND: {key} -> {name}")
                found = True
        
        if not found:
            print("No matches for Aya or Mohammed in campaign_registry.json")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
