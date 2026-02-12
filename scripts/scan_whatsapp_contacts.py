
import os
import json
import re

DATA_DIR = "data"
EXPORTS_DIR = os.path.join(DATA_DIR, "exports")
POTENTIAL_BENEFICIARIES_FILE = os.path.join(DATA_DIR, "potential_beneficiaries.json")
WHATSAPP_LIVE_EXTRACT = os.path.join(DATA_DIR, "whatsapp_live_extract.txt")

def extract_numbers(text):
    # Match various phone number formats (972..., 970..., etc.)
    # This is a broad regex to catch common formats in the logs
    return re.findall(r'\b(?:\+?\d{1,3}[- _]?)?\d{2,3}[- _]?\d{3}[- _]?\d{4}\b', text)

def clean_number(num):
    # Remove non-digits
    return re.sub(r'\D', '', num)

def get_existing_numbers():
    if not os.path.exists(POTENTIAL_BENEFICIARIES_FILE):
        return set()
    with open(POTENTIAL_BENEFICIARIES_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return {clean_number(b['name']) for b in data if any(c.isdigit() for c in b['name'])}

def scan_exports():
    found_numbers = set()
    if os.path.exists(EXPORTS_DIR):
        for filename in os.listdir(EXPORTS_DIR):
            # Extract from filename
            nums = extract_numbers(filename)
            for n in nums:
                found_numbers.add(clean_number(n))
            
            # Extract from file content (only for .txt and .json files)
            if filename.endswith(('.txt', '.json')):
                try:
                    with open(os.path.join(EXPORTS_DIR, filename), 'r', encoding='utf-8') as f:
                        content = f.read()
                        nums = extract_numbers(content)
                        for n in nums:
                            found_numbers.add(clean_number(n))
                except:
                    continue
    return found_numbers

def scan_live_extract():
    found_numbers = set()
    if os.path.exists(WHATSAPP_LIVE_EXTRACT):
        try:
            with open(WHATSAPP_LIVE_EXTRACT, 'r', encoding='utf-8') as f:
                content = f.read()
                nums = extract_numbers(content)
                for n in nums:
                    found_numbers.add(clean_number(n))
        except:
            pass
    return found_numbers

def main():
    existing = get_existing_numbers()
    from_exports = scan_exports()
    from_live = scan_live_extract()
    
    all_found = from_exports.union(from_live)
    
    # Filter for numbers that look like valid Gaza/Palestine/Israel numbers
    # (Starting with 972 or 970, or local 05...)
    # We also want to exclude very short or very long strings that might be captured
    filtered = set()
    for n in all_found:
        if 9 <= len(n) <= 15:
            if n.startswith(('972', '970', '05')):
                filtered.add(n)
    
    new_numbers = filtered - existing
    
    print(f"Total numbers found: {len(all_found)}")
    print(f"Filtered (Palestine/Israel) numbers: {len(filtered)}")
    print(f"Existing numbers: {len(existing)}")
    print(f"New numbers found: {len(new_numbers)}")
    
    results = sorted(list(new_numbers))
    
    # Output as a new onboarding list format
    onboarding_list = []
    for num in results:
        onboarding_list.append({
            "name": num,
            "status": "Potential",
            "source": "WhatsApp Scan"
        })
    
    with open(os.path.join(DATA_DIR, "new_whatsapp_onboarding_list.json"), 'w', encoding='utf-8') as f:
        json.dump(onboarding_list, f, indent=2)
    
    print(f"\nSaved {len(onboarding_list)} new potential beneficiaries to data/new_whatsapp_onboarding_list.json")

if __name__ == "__main__":
    main()
