import json
import re

LEDGER_FILE = "data/internal_ledger.json"

def check_keys():
    with open(LEDGER_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    keys = list(data.keys())
    print(f"Total keys: {len(keys)}")
    
    # Check for 'Abu'
    abus = [k for k in keys if "Abu" in k]
    print(f"Keys containing 'Abu': {abus}")
    
    # Check for policy compliance (Title Case, no spaces ideally? Or Space-###?)
    # Generally Name-###
    
    violations = []
    for k in keys:
        if not re.match(r"^[A-Z][a-zA-Z\s\-\']+(\-\d{3})?$", k):
            violations.append(k)
            
    print(f"\nPotential Format Violations ({len(violations)}):")
    for v in violations[:20]:
        print(v)

if __name__ == "__main__":
    check_keys()
