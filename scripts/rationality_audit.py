
import json
import os
import re

DATA_DIR = "data"
INPUT_FILE = os.path.join(DATA_DIR, "potential_growth_list.json")
OUTPUT_FILE = os.path.join(DATA_DIR, "potential_growth_list_audited.json")
OUTBOX_DIR = os.path.join(DATA_DIR, "onboarding_outbox")

def is_rational(bid, name):
    # 1. Basic cleaning - get ONLY digits
    clean_id = re.sub(r'\D', '', bid)
    bid_lower = bid.lower()
    
    # --- STRICT NUMERIC-ONLY POLICY ---
    # People we don't know = Phone numbers. No names allowed in new expansion discovery.
    if not clean_id or len(clean_id) < 9:
        return False, "Not a phone number (Too short/No digits)"

    # 2. Regional Filter (Strict)
    # Valid regional codes: 972 (Israel/Gaza), 970 (Palestine), or local 05...
    if not clean_id.startswith(('972', '970', '05')):
         return False, "Non-regional number"

    # 3. Size/Length Test
    if len(clean_id) > 15:
        return False, "Too long (Not a standard number)"

    # 4. Noise/Syntax Test
    if "unknown" in bid_lower:
        return False, "Unknown placeholder"
    
    # Generic noise keywords (even if they have numbers)
    if any(k in bid_lower for k in ['photo', 'welcome', 'status', 'settings', 'group_invite', 'deleted']):
        return False, "System noise"
    
    # Link noise
    if "http" in bid_lower or "www" in bid_lower:
        return False, "URL/Link noise"

    return True, "OK (Valid Phone Number)"

def main():
    if not os.path.exists(INPUT_FILE):
        print("Input file not found.")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        contacts = json.load(f)

    audited = []
    rejected = []

    for c in contacts:
        rational, reason = is_rational(c['id'], c['name'])
        if rational:
            audited.append(c)
        else:
            rejected.append({"name": c['name'], "reason": reason})

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(audited, f, indent=2)

    print(f"Audit Complete:")
    print(f" - Original: {len(contacts)}")
    print(f" - Audited (Clean): {len(audited)}")
    print(f" - Rejected (Crap): {len(rejected)}")
    
    # Clean Outbox
    # We only want to keep outbox messages that correspond to audited IDs
    if os.path.exists(OUTBOX_DIR):
        clean_ids = {re.sub(r'[^a-zA-Z0-9]', '_', c['id']) + "_onboarding.txt" for c in audited}
        files_removed = 0
        for f in os.listdir(OUTBOX_DIR):
            if f not in clean_ids:
                try:
                    os.remove(os.path.join(OUTBOX_DIR, f))
                    files_removed += 1
                except: continue
        print(f" - Outbox cleaned: {files_removed} crap messages removed.")

    if rejected:
        print("\nSample Rejections:")
        for r in rejected[:10]:
            print(f"   - {r['name']} ({r['reason']})")

if __name__ == "__main__":
    main()
