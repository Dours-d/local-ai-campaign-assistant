
import os
import re
import json

CAMPAIGNLESS_FILE = "data/campaignless_whatsapp.txt"
OUTBOX_DIR = "data/onboarding_outbox"

def validate():
    if not os.path.exists(CAMPAIGNLESS_FILE):
        print(f"Error: {CAMPAIGNLESS_FILE} not found.")
        return

    if not os.path.exists(OUTBOX_DIR):
        print(f"Error: {OUTBOX_DIR} not found.")
        return

    # 1. Parse campaignless numbers
    with open(CAMPAIGNLESS_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract numbers like +972 59-746-5525
    numbers = re.findall(r"\+(\d[\d\s\-]*)", content)
    sanitized_numbers = []
    for num in numbers:
        # Sanitize to digits only
        sanitized = "".join([c for c in num if c.isdigit()])
        if sanitized:
            sanitized_numbers.append(sanitized)
    
    print(f"Found {len(sanitized_numbers)} numbers in campaignless file.")

    # 2. Check outbox files
    outbox_files = os.listdir(OUTBOX_DIR)
    outbox_numbers = [f.replace(".txt", "") for f in outbox_files if f.endswith(".txt")]
    
    missing = []
    for num in sanitized_numbers:
        if num not in outbox_numbers:
            missing.append(num)
    
    if missing:
        print(f"WARNING: {len(missing)} numbers are missing from outbox:")
        for m in missing:
            print(f"  - {m}")
    else:
        print("SUCCESS: All campaignless numbers have an outbox file.")

    # 3. Check for unique USDT addresses and correct links
    addresses = {} # addr -> [numbers]
    links = {} # num -> link
    
    for f in outbox_files:
        if not f.endswith(".txt"): continue
        num = f.replace(".txt", "")
        path = os.path.join(OUTBOX_DIR, f)
        with open(path, 'r', encoding='utf-8') as file:
            body = file.read()
            
            # Extract USDT address
            addr_match = re.search(r"0x[a-fA-F0-9]{40}", body)
            if addr_match:
                addr = addr_match.group(0)
                if addr not in addresses:
                    addresses[addr] = []
                addresses[addr].append(num)
            else:
                print(f"ERROR: No USDT address found in {f}")

            # Extract personalized link
            link_match = re.search(r"https://dours-d\.github\.io/local_ai_campaign_assistant/docs/onboard\.html\?u=(.*)", body)
            if link_match:
                links[num] = link_match.group(1).strip()
            else:
                # English version might be different
                link_match_en = re.search(r"https://dours-d\.github\.io/local_ai_campaign_assistant/docs/onboard\.html/(.*)", body)
                if link_match_en:
                     links[num] = link_match_en.group(1).strip()
                else:
                    print(f"ERROR: No personalized link found in {f}")

    # Check for duplicate addresses
    duplicates = {addr: nums for addr, nums in addresses.items() if len(nums) > 1}
    if duplicates:
        print(f"ERROR: {len(duplicates)} duplicate USDT addresses found!")
        for addr, nums in duplicates.items():
            print(f"  - {addr}: used by {nums}")
    else:
        print("SUCCESS: All USDT addresses are unique.")

    print(f"Validated {len(outbox_numbers)} files in outbox.")

if __name__ == "__main__":
    validate()
