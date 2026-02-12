
import os
import json
import re

DATA_DIR = "data"
POTENTIAL_BENEFICIARIES_FILE = os.path.join(DATA_DIR, "potential_beneficiaries.json")
WHATSAPP_LIVE_EXTRACT = os.path.join(DATA_DIR, "whatsapp_live_extract.txt")

def clean_number(num):
    return re.sub(r'\D', '', num)

def get_existing_numbers():
    if not os.path.exists(POTENTIAL_BENEFICIARIES_FILE):
        return set()
    with open(POTENTIAL_BENEFICIARIES_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        existing = set()
        for b in data:
            cleaned = clean_number(b['name'])
            if cleaned:
                existing.add(cleaned)
        return existing

def main():
    existing = get_existing_numbers()
    
    if not os.path.exists(WHATSAPP_LIVE_EXTRACT):
        print("Live extract not found.")
        return

    with open(WHATSAPP_LIVE_EXTRACT, 'r', encoding='utf-8') as f:
        content = f.read()

    # Look for patterns like [+972 59-717-2654] or just the number
    pattern = r'(\+?[\d\-\_\ ]{9,18})'
    
    # We want to find matches and their context
    matches = re.finditer(pattern, content)
    
    new_found = {} # number -> context
    
    for m in matches:
        raw = m.group(0)
        cleaned = clean_number(raw)
        
        if 9 <= len(cleaned) <= 15:
            if cleaned.startswith(('972', '970', '05', '59', '56')):
                if cleaned not in existing:
                    # Check for 05... vs 972...
                    if cleaned.startswith('05'):
                        if ('972' + cleaned[1:]) in existing or ('970' + cleaned[1:]) in existing:
                            continue
                    
                    # New number!
                    # Get surrounding context (100 chars before and after)
                    start = max(0, m.start() - 100)
                    end = min(len(content), m.end() + 100)
                    context = content[start:end].replace('\n', ' ')
                    
                    if cleaned not in new_found:
                        new_found[cleaned] = context
    
    print(f"Found {len(new_found)} potential new contacts in live extract.\n")
    
    results = []
    for num, ctx in new_found.items():
        print(f"Number: {num}")
        print(f"Context: ...{ctx}...")
        print("-" * 40)
        results.append({"name": num, "context": ctx})
        
    with open(os.path.join(DATA_DIR, "new_contacts_from_live_extract.json"), 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
