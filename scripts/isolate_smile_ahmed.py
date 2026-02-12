import json
import os
import csv

LEDGER_FILE = 'data/internal_ledger.json'
CAMPAIGNS_UNIFIED = 'data/campaigns_unified.json'
OUTPUT_DIR = 'data/isolated/the_ahmed_smile'
LEDGER_OUTPUT = os.path.join(OUTPUT_DIR, 'smile_ahmed_ledger.json')
DEBT_OUTPUT = os.path.join(OUTPUT_DIR, 'smile_ahmed_debts.json')

def isolate_smile_ahmed():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # 1. Isolate Ledger (Key is 'Lets')
    with open(LEDGER_FILE, 'r', encoding='utf-8') as f:
        ledger = json.load(f)
    
    smile_data = ledger.get('Lets', {})
    with open(LEDGER_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump({'Lets': smile_data}, f, indent=4)

    # 2. Isolate Debts (Using hint matching 'smile' or 'lets')
    import sys
    sys.path.append('scripts')
    import generate_debt_table as debt_source
    
    all_debts = debt_source.get_all_debts()
    smile_debts = [d for d in all_debts if 'smile' in d['hint'].lower() or 'lets' in d['hint'].lower()]
    
    with open(DEBT_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(smile_debts, f, indent=4)
        
    print(f"Isolated Smile Ahmed (Lets) to {OUTPUT_DIR}")

if __name__ == "__main__":
    isolate_smile_ahmed()
