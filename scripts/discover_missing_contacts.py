
import os
import json
import re

DATA_DIR = "data"
EXPORTS_DIR = os.path.join(DATA_DIR, "exports")
POTENTIAL_BENEFICIARIES_FILE = os.path.join(DATA_DIR, "potential_beneficiaries.json")
OUTREACHED_FILE = os.path.join(DATA_DIR, "outreached_today.txt")

def normalize(name):
    return name.strip('_').strip().strip('[]').lower()

def is_script_or_noise(path, content):
    content_lower = content.lower()
    if "param(" in content_lower or "function " in content_lower or "send-cdpcommand" in content_lower:
        return True
    if "[system.net" in content_lower or "start-sleep" in content_lower:
        return True
    if len(content.strip()) < 50:
        return True
    if content.strip().startswith("<#") or "whatsapp business chat exporter" in content_lower:
        return True
    return False

def is_rational(bid, name):
    # 1. Basic cleaning - get ONLY digits
    clean_id = re.sub(r'\D', '', bid)
    bid_lower = bid.lower()
    
    # --- NOISE FILTER (Messages vs IDs) ---
    # If the filename contains too many underscores or spaces without numbers, it's likely a message
    if len(re.findall(r'[a-zA-Z]', bid)) > 15: # Too much text
         # Still allow if it starts with Trustee (already processed)
         if not bid_lower.startswith('trustee'):
            return False

    # 2. Strict Numeric Policy for Discovery
    if not clean_id or len(clean_id) < 9:
        return False

    # 3. Regional Filter (Strict) - uniquely +972, +970, +967 (Yemen) or local 05...
    if not clean_id.startswith(('972', '970', '967', '05')):
         return False

    # 4. Size/Length Test
    if len(clean_id) > 15:
        return False

    # 5. Keywords/Noise
    if any(k in bid_lower for k in ['photo', 'welcome', 'status', 'settings', 'group_invite', 'deleted', 'please', 'help', 'brother']):
        return False
    if "http" in bid_lower or "www" in bid_lower:
        return False

    return True

def get_exclusion_list():
    exclusions = set()
    
    def add_to_exclusions(val):
        if not val: return
        norm = normalize(str(val))
        exclusions.add(norm)
        clean = re.sub(r'\D', '', norm)
        if clean: exclusions.add(clean)

    # 1. Existing Beneficiaries
    if os.path.exists(POTENTIAL_BENEFICIARIES_FILE):
        with open(POTENTIAL_BENEFICIARIES_FILE, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                for b in data:
                    add_to_exclusions(b.get('id'))
                    add_to_exclusions(b.get('name'))
            except: pass

    # 2. Unified Campaigns (The "Already Onboarded" source)
    UNIFIED_FILE = os.path.join(DATA_DIR, "campaigns_unified.json")
    if os.path.exists(UNIFIED_FILE):
        with open(UNIFIED_FILE, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                entries = data.items() if isinstance(data, dict) else [(None, e) for e in data]
                for _, entry in entries:
                    bid = entry.get('beneficiary_id') or entry.get('id')
                    add_to_exclusions(bid)
                    iname = entry.get('internal_name')
                    add_to_exclusions(iname)
            except: pass

    # 3. Onboarding Outbox (Check if message was already generated)
    OUTBOX_DIR = os.path.join(DATA_DIR, "onboarding_outbox")
    if os.path.exists(OUTBOX_DIR):
        for f in os.listdir(OUTBOX_DIR):
            if f.endswith('.txt'):
                clean_f = f.replace('_onboarding.txt', '').replace('_campaign_PENDING.txt', '')
                add_to_exclusions(clean_f)
                try:
                    with open(os.path.join(OUTBOX_DIR, f), 'r', encoding='utf-8') as content_file:
                        content = content_file.read()
                        ids_in_file = re.findall(r'ID: (\d+)', content)
                        for found_id in ids_in_file:
                            add_to_exclusions(found_id)
                except: pass

    # 4. Manual Exclusion / Outreach log
    if os.path.exists(OUTREACHED_FILE):
        with open(OUTREACHED_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip(): add_to_exclusions(line.strip())
                
    return exclusions

def main():
    exclusions = get_exclusion_list()
    print(f"Loaded {len(exclusions)} unique exclusion keys (redundancy check).")
    
    if not os.path.exists(EXPORTS_DIR):
        print("Exports directory not found.")
        return

    discovered = []
    seen_normalized = set()
    
    for f in os.listdir(EXPORTS_DIR):
        if f.endswith(('.json', '.txt', '.html')):
            base = f.rsplit('.', 1)[0]
            norm = normalize(base)
            clean_digits = re.sub(r'\D', '', norm)
            
            # CHECK EXCLUSIONS ROBUSTLY
            if not norm or norm in exclusions or clean_digits in exclusions or norm in seen_normalized:
                continue
            
            # --- RATIONALITY & REGIONAL TEST ---
            if not is_rational(norm, base):
                continue

            try:
                path = os.path.join(EXPORTS_DIR, f)
                if f.endswith('.txt') or f.endswith('.html'):
                    with open(path, 'r', encoding='utf-8', errors='ignore') as content_file:
                        content = content_file.read(2000)
                        if is_script_or_noise(path, content):
                            continue
            except:
                continue
            
            seen_normalized.add(norm)
            discovered.append({
                "name": base.strip('_'),
                "id": norm,
                "category": "Growth",
                "status": "Potential",
                "source": "WhatsApp Export Sync"
            })

    # --- PART 2: SCAN LIVE EXTRACTS ---
    AUX_FILES = [
        os.path.join(DATA_DIR, "whatsapp_live_extract.txt"),
        os.path.join(DATA_DIR, "whatsapp_no_campaign.txt"),
        os.path.join(DATA_DIR, "campaignless_whatsapp.txt")
    ]
    
    for aux_path in AUX_FILES:
        if os.path.exists(aux_path):
            try:
                with open(aux_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    # Find potential numbers (9-15 digits, regional prefixes)
                    # This pattern matches numbers with optional + and separators
                    potential_nums = re.findall(r'(?:\+?[\d\-\_\ ]{9,18})', content)
                    for raw_num in potential_nums:
                        clean_digits = re.sub(r'\D', '', raw_num)
                        norm = normalize(clean_digits)
                        
                        # Apply same strict filters as exports
                        if not norm or norm in exclusions or clean_digits in exclusions or norm in seen_normalized:
                            continue
                            
                        if not is_rational(norm, raw_num):
                            continue
                            
                        seen_normalized.add(norm)
                        discovered.append({
                            "name": norm,
                            "id": norm,
                            "category": "Growth",
                            "status": "Potential",
                            "source": f"Live Extract ({os.path.basename(aux_path)})"
                        })
            except Exception as e:
                print(f"Error scanning {aux_path}: {e}")

    discovered.sort(key=lambda x: x['name'])

    output_file = os.path.join(DATA_DIR, "potential_growth_list.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(discovered, f, indent=2)
    
    print(f"Found {len(discovered)} new potential contacts after deep redundancy check.")

if __name__ == "__main__":
    main()
