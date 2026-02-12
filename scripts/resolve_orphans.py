
import json
import os

def load_json(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def main():
    registry = load_json('data/campaign_registry.json').get('mappings', {})
    
    # Phone numbers to look for
    target_phones = [
        '+970594591409', # Hanin
        '+972599224585', # Ibtisam
        '+972567662571', # Ibtisam (survive)
        '+972599507376', # Walid
        '+972595089384', # Khaled
    ]
    
    print("--- IDENTIFIED TRUSTEES ---")
    for phone in target_phones:
        found = False
        for k, v in registry.items():
            if v.get('whatsapp') == phone:
                print(f"Phone {phone} -> {v['name']} ({k})")
                found = True
                break
        if not found:
            print(f"Phone {phone} -> NOT FOUND in Registry")

if __name__ == "__main__":
    main()
