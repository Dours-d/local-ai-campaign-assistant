import json
import os
import re

DATA_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UNIFIED_PATH = os.path.join(DATA_DIR, "data", "campaigns_unified.json")

def audit_abu_umm():
    with open(UNIFIED_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    campaigns = data.get("campaigns", [])
    
    standard_prefixes = ["umm", "um", "om", "abu", "aba", "abi", "bin", "bint"]

    for c in campaigns:
        privacy = c.get("privacy", {})
        first_name = str(privacy.get("first_name", "")).strip()
        internal_name = privacy.get("internal_name", "")
        
        parts = first_name.split()
        if len(parts) > 1:
            prefix = parts[0].lower()
            if prefix in standard_prefixes:
                fname_group = f"{parts[0]} {parts[1]}"
                is_prefix_name = True
                
                # Check if it SHOULD be suffixed
                pattern = re.compile(f"^{re.escape(fname_group)}-(\\d{{3}})$")
                has_suffix = bool(pattern.match(internal_name))
                
                if not has_suffix:
                    print(f"Candidate for suffix: '{first_name}' (Current: '{internal_name}') -> Group: '{fname_group}'")

if __name__ == "__main__":
    audit_abu_umm()
