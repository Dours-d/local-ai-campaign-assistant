
import json
import os
import sys

# Sibling import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import generate_debt_table as debt_source

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
LEDGER_FILE = os.path.join(DATA_DIR, 'internal_ledger.json')

def load_ledger():
    if not os.path.exists(LEDGER_FILE): return {}
    with open(LEDGER_FILE, 'r', encoding='utf-8') as f: return json.load(f)

def debug_orphans():
    ledger = load_ledger()
    debts_list = debt_source.get_all_debts()
    
    HINT_TO_KEY = {
        "Mahmoud-002": "Mahmoud-002",
        "Mahmoud": "Mahmoud-002",
        "Mahmod": "Mahmoud-002",
        "Noor-001": "Noor-001",
        "Noor": "Noor-001",
        "Mohammed": "Mohammed-011",
        "Mohammed-011": "Mohammed-011",
        "Suhail": "Mohammed-011",
        "Zina": "Zina-001",
        "Zina-001": "Zina-001",
        "Hala": "Hala-002",
        "Hala-002": "Hala-002",
        "Rania": "Rania",
        "Fayezs": "Fayezs",
        "Fayez": "Fayezs",
        "Samirah": "Samirah"
    }

    print("--- ORPHAN AUDIT ---")
    print(f"Total Debts Scanned: {len(debts_list)}")
    
    unmapped = []
    mapped_count = 0
    
    for item in debts_list:
        hint = item['hint']
        amt = item['amount']
        
        matched_key = HINT_TO_KEY.get(hint)
        if not matched_key:
            if hint in ledger:
                matched_key = hint
            else:
                for l_key in ledger.keys():
                    if l_key.lower().startswith(hint.lower()):
                        matched_key = l_key
                        break
        
        if matched_key:
            mapped_count += 1
        else:
            unmapped.append(item)

    print(f"Mapped: {mapped_count}")
    print(f"Orphans: {len(unmapped)}")
    print("\n--- ORPHAN DETAILS ---")
    total_orphan = 0
    for item in unmapped:
        print(f"Amount: €{item['amount']:.2f} | Hint: {item['hint']} | Campaign: {item['campaign']}")
        total_orphan += item['amount']
        
    print(f"\nTOTAL ORPHAN LIABILITY: €{total_orphan:.2f}")

if __name__ == "__main__":
    debug_orphans()
