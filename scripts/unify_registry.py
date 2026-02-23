import json
import csv
import re
import os

def normalize_phone(phone):
    if not phone:
        return None
    # Strip everything except digits
    clean = re.sub(r'\D', '', str(phone))
    # Handle common prefix variations (e.g., 00972 -> 972)
    if clean.startswith('00'):
        clean = clean[2:]
    return clean

def load_json(path):
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except:
            return []

def load_csv(path):
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def unify():
    # Detect Vault vs Public Data
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    vault_dir = os.path.join(base_dir, 'vault')
    data_dir = os.path.join(base_dir, 'data')
    
    is_private = os.path.exists(vault_dir)
    root_src = vault_dir if is_private else data_dir
    
    growth_list_path = os.path.join(root_src, 'final_real_growth_list.json')
    registry_path = os.path.join(root_src, 'campaign_registry.json')
    return_links_path = os.path.join(root_src, 'whydonate_return_links.csv')
    creation_log_path = os.path.join(root_src, 'whydonate_creation_log.json')
    wd_links_txt_path = os.path.join(root_src, 'all_wd_links.txt')
    output_path = os.path.join(root_src, 'UNIFIED_REGISTRY.json')
    
    if not is_private:
        print("!!! RUNNING IN PUBLIC DEMO MODE (VAULT MISSING) !!!")
        print(f"Using source: {data_dir}")

    growth_data = load_json(growth_list_path)
    registry_data = load_json(registry_path)
    if isinstance(registry_data, dict) and 'mappings' in registry_data:
        registry_mappings = registry_data['mappings']
    else:
        registry_mappings = {}
    
    return_links = load_csv(return_links_path)
    creation_log = load_json(creation_log_path)

    unified = {} # Key: normalized_phone

    # Phase 1: Base Growth List (Chuffed/Intake)
    for entry in growth_data:
        raw_wa = entry.get('whatsapp')
        norm_wa = normalize_phone(raw_wa)
        if not norm_wa:
            continue
        
        if norm_wa not in unified:
            unified[norm_wa] = {
                "whatsapp": raw_wa,
                "norm_whatsapp": norm_wa,
                "title": entry.get('title', ''),
                "description": entry.get('description', ''),
                "goal": entry.get('goal', 5000),
                "status": entry.get('status', 'verified'),
                "bids": [entry.get('bid')],
                "image": entry.get('image', ''),
                "validation_source": entry.get('validation_source', ''),
                "whydonate_url": entry.get('whydonate_url', None),
                "identity_indices": entry.get('identity_indices', [0, 1]),
                "registry_name": entry.get('registry_name', None),
                "ishmael_id": entry.get('ishmael_id', None)
            }
        else:
            unified[norm_wa]["bids"].append(entry.get('bid'))

    # Helper: Title Clean for matching
    def clean_title(t):
        if not t: return ""
        # Remove common "Help" prefix, bombs, families, rebuild, survive, gaza
        return re.sub(r'[^a-zA-Z0-9]', '', t.lower().replace('help', '').replace('gaza', '').replace('family', ''))

    # Phase 2: Layer in WhyDonate Creation Log (Dynamic extraction)
    wd_discovered = {} # title_clean -> url
    current_title = ""
    for state_entry in creation_log:
        state = state_entry.get('state', {})
        url = state.get('url', '')
        
        # Look for Title inputs
        inputs = state.get('inputs', [])
        for inp in inputs:
            if inp.get('placeholder') == 'Fundraiser Title':
                val = inp.get('value')
                if val: current_title = val
        
        # If we see a live fundraising URL, map the last seen title to it
        if "/fundraising/" in url and not url.endswith('/create') and not url.endswith('/start'):
            clean_t = clean_title(current_title)
            if clean_t:
                wd_discovered[clean_t] = url

    # Phase 3: Layer in return links CSV + all_wd_links.txt
    if os.path.exists(wd_links_txt_path):
        with open(wd_links_txt_path, 'r', encoding='utf-8') as f:
            for line in f:
                match = re.search(r'"whydonate_url":\s*"(https://whydonate.com/fundraising/[^"]+)"', line)
                if match:
                    url = match.group(1)
                    # Extract title from URL slug
                    slug = url.split('/')[-1].replace('-', ' ')
                    wd_discovered[clean_title(slug)] = url

    # Apply Discovered WhyDonate links to Growth Data
    for norm_wa, entry in unified.items():
        clean_t = clean_title(entry.get('title'))
        reg_name_clean = clean_title(entry.get('registry_name'))
        
        # Match by Title
        if clean_t in wd_discovered:
            entry["whydonate_url"] = wd_discovered[clean_t]
            entry["status"] = "live"
            continue
            
        # Match by Registry Name (fuzzy)
        if reg_name_clean:
            for wd_t_clean, url in wd_discovered.items():
                if reg_name_clean in wd_t_clean or wd_t_clean in reg_name_clean:
                    entry["whydonate_url"] = url
                    entry["status"] = "live"
                    break

    # Phase 4: Pivot by Registry (Primary source for IDs/Urls)
    for key, reg in registry_mappings.items():
        wa = reg.get('whatsapp')
        norm_wa = normalize_phone(wa)
        if not norm_wa:
            continue
            
        wd_url = reg.get('whydonate_url')
        if wd_url:
            if norm_wa in unified:
                unified[norm_wa]["whydonate_url"] = wd_url
                unified[norm_wa]["status"] = "live"
            else:
                unified[norm_wa] = {
                    "whatsapp": wa,
                    "norm_whatsapp": norm_wa,
                    "title": reg.get('name', 'Live Campaign'),
                    "description": "",
                    "goal": 5000,
                    "status": "live",
                    "bids": [f"reg_{key}"],
                    "image": "",
                    "validation_source": "registry",
                    "whydonate_url": wd_url,
                    "identity_indices": [0, 1],
                    "registry_name": reg.get('name'),
                    "wallet_address": reg.get('wallet_address')
                }

    # Phase 5: Layer in Return Links CSV (Final fallback)
    for link in return_links:
        wa = link.get('whatsapp_number')
        norm_wa = normalize_phone(wa)
        if not norm_wa:
            continue
            
        wd_url = link.get('whydonate_url')
        if wd_url and wd_url.startswith('http'):
            entry = unified.get(norm_wa)
            if entry:
                entry["whydonate_url"] = wd_url
                entry["status"] = "live"

    # Export
    output_list = list(unified.values())
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_list, f, indent=4, ensure_ascii=False)
    
    print(f"Unification complete. Total unique beneficiaries: {len(output_list)}")
    live_count = sum(1 for e in output_list if e.get('status') == 'live')
    print(f"Live on WhyDonate: {live_count}")
    print(f"Verified for Creation: {len(output_list) - live_count}")

if __name__ == "__main__":
    unify()
