import json
import os

LEDGER_FILE = 'data/internal_ledger.json'
OUTPUT_DIR = 'data/isolated/ahmed'
LEDGER_OUTPUT = os.path.join(OUTPUT_DIR, 'ahmed_ledger.json')
DEBT_OUTPUT = os.path.join(OUTPUT_DIR, 'ahmed_debts.json')

# Import siblings to get debts
import sys
sys.path.append('scripts')
import generate_debt_table as debt_source

def isolate_ahmed():
    # 1. Isolate Ledger
    with open(LEDGER_FILE, 'r', encoding='utf-8') as f:
        ledger = json.load(f)
    
    ahmed_ledger = {k: v for k, v in ledger.items() if 'ahmed' in k.lower()}
    
    with open(LEDGER_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(ahmed_ledger, f, indent=4)
    
    # 2. Isolate Debts
    all_debts = debt_source.get_all_debts()
    ahmed_debts = [d for d in all_debts if 'ahmed' in d['hint'].lower()]
    
    with open(DEBT_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(ahmed_debts, f, indent=4)
    
    print(f"Isolated {len(ahmed_ledger)} ledger keys and {len(ahmed_debts)} debt items to {OUTPUT_DIR}")

if __name__ == "__main__":
    isolate_ahmed()
