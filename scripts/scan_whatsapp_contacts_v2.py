
import os
import json
import re

DATA_DIR = "data"
EXPORTS_DIR = os.path.join(DATA_DIR, "exports")
POTENTIAL_BENEFICIARIES_FILE = os.path.join(DATA_DIR, "potential_beneficiaries.json")
WHATSAPP_LIVE_EXTRACT = os.path.join(DATA_DIR, "whatsapp_live_extract.txt")

def extract_numbers_broad(text):
    # Match any sequence of 9-15 digits, optionally with separators
    # This is broad to catch numbers inside text or mixed with other characters
    # Look for sequences that look like phone numbers
    pattern = r'(?:\+?[\d\-\_\ ]{9,18})'
    candidates = re.findall(pattern, text)
    
    found = []
    for c in candidates:
        cleaned = re.sub(r'\D', '', c)
        if 9 <= len(cleaned) <= 15:
            # Common prefixes for the region
            if cleaned.startswith(('972', '970', '05', '59', '56')):
                # Normalize 05... to 9725... or 9705... if we can assume local context
                # But for now, just keep the digits as is for matching
                found.append(cleaned)
    return found

def get_existing_numbers():
    if not os.path.exists(POTENTIAL_BENEFICIARIES_FILE):
        return set()
    with open(POTENTIAL_BENEFICIARIES_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        existing = set()
        for b in data:
            cleaned = re.sub(r'\D', '', b['name'])
            if cleaned:
                existing.add(cleaned)
        return existing

def scan_file(filepath):
    found = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            found.extend(extract_numbers_broad(content))
    except:
        pass
    return found

def main():
    existing = get_existing_numbers()
    all_found = set()
    
    # Scan Exports
    if os.path.exists(EXPORTS_DIR):
        for filename in os.listdir(EXPORTS_DIR):
            # Filename itself
            all_found.update(extract_numbers_broad(filename))
            # File content
            if filename.endswith(('.txt', '.json', '.html')):
                all_found.update(scan_file(os.path.join(EXPORTS_DIR, filename)))
    
    # Scan Live Extract
    if os.path.exists(WHATSAPP_LIVE_EXTRACT):
        all_found.update(scan_file(WHATSAPP_LIVE_EXTRACT))
        
    # Scan other potential files
    other_files = [
        "whatsapp_no_campaign.txt",
        "campaignless_whatsapp.txt",
        "whatsapp_live_extract.csv",
        "whatsapp_chats.json"
    ]
    for f in other_files:
        p = os.path.join(DATA_DIR, f)
        if os.path.exists(p):
            all_found.update(scan_file(p))
            
    # Filter and Normalize
    # We'll normalize 05... to 9725... (or 9705... whichever is more common in existing)
    # Actually, it's safer to just look at what's NEW.
    
    new_numbers = set()
    for n in all_found:
        if n not in existing:
            # Double check with leading '972' if it's '05...'
            if n.startswith('05'):
                alt1 = '972' + n[1:]
                alt2 = '970' + n[1:]
                if alt1 not in existing and alt2 not in existing:
                    new_numbers.add(n)
            else:
                new_numbers.add(n)
                
    print(f"Total unique numbers found: {len(all_found)}")
    print(f"Existing numbers (cleaned): {len(existing)}")
    print(f"New potential numbers: {len(new_numbers)}")
    
    results = sorted(list(new_numbers))
    
    onboarding_list = []
    for num in results:
        onboarding_list.append({
            "name": num,
            "status": "Potential",
            "source": "WhatsApp Comprehensive Scan"
        })
    
    with open(os.path.join(DATA_DIR, "new_whatsapp_onboarding_list_v2.json"), 'w', encoding='utf-8') as f:
        json.dump(onboarding_list, f, indent=2)
    
    print(f"\nSaved v2 list to data/new_whatsapp_onboarding_list_v2.json")
    if results:
        print(f"Sample new numbers: {results[:10]}")

if __name__ == "__main__":
    main()
