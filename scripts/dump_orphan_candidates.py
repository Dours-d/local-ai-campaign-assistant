
import json
import os

def load_json(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def main():
    ledger = load_json('data/internal_ledger.json')
    registry = load_json('data/campaign_registry.json').get('mappings', {})
    
    targets = ['hanin', 'ibtisam', 'khaled', 'walid', 'rami', 'lian', 'hisham', 'hassan', 'ahmed']
    
    print("--- LEDGER MATCHES ---")
    for k, v in ledger.items():
        if any(t in k.lower() for t in targets):
            print(f"Key: {k}")
            print(f"  Campaigns: {v.get('campaigns', [])}")
            print(f"  Raised: {v.get('raised_gross_eur', 0)}")
            
    print("\n--- REGISTRY MATCHES ---")
    for k, v in registry.items():
        name = v.get('name', '').lower()
        if any(t in name for t in targets):
            print(f"Key: {k}")
            print(f"  Name: {v.get('name')}")
            print(f"  WhatsApp: {v.get('whatsapp')}")
            print(f"  Wallet: {v.get('wallet_address')}")

if __name__ == "__main__":
    main()
