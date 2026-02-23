import re
import json

def cross_reference_audit():
    with open('campaign_index_full.json', 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    with open('onboarding_messages.txt', 'r', encoding='utf-8') as f:
        messages_content = f.read()
    
    # Split messages by the separator
    messages = re.split(r'-{30,}', messages_content)
    
    print(f"Auditing {len(messages)} message blocks against Registry...\n")
    
    missing_individual_links = []
    id_mismatches = []
    
    for block in messages:
        if not block.strip():
            continue
            
        # Extract ID (usually after "FOR " or on its own line)
        id_match = re.search(r'MESSAGE FOR ([a-zA-Z0-9_+:-]+)', block)
        if not id_match:
            # Try to find ID on its own line
            lines = block.strip().split('\n')
            if lines and re.match(r'^[a-zA-Z0-9_+:-]+$', lines[0]):
                beneficiary_id = lines[0]
            else:
                continue
        else:
            beneficiary_id = id_match.group(1)
            
        # Check if this ID is in the registry
        registry_entry = None
        # Registry keys are phones like "+972..." but messages might use the ID
        for phone, entry in registry.items():
            if phone == beneficiary_id or entry.get('beneficiary_id') == beneficiary_id:
                registry_entry = entry
                beneficiary_phone = phone
                break
        
        if registry_entry:
            # Does the registry have a WhyDonate link?
            wd_url = registry_entry.get('whydonate', {}).get('url')
            if wd_url:
                # Is this link present in the message block?
                if wd_url not in block:
                    missing_individual_links.append(f"ID: {beneficiary_id} | Phone: {beneficiary_phone} | Missing individual link: {wd_url}")
        else:
            # Message exists for an ID not in the truth layer
            id_mismatches.append(f"ORPHAN MESSAGE: {beneficiary_id}")

    print("="*50)
    if missing_individual_links:
        print(f"DECEPTION GAP DETECTED: {len(missing_individual_links)} messages are using 'Umbrella Fund' instead of their registered WhyDonate links.")
        for item in missing_individual_links:
            print(f"  - {item}")
    else:
        print("ALL MESSAGES SYNCED: Every registered WhyDonate link is present in the messages.")
        
    if id_mismatches:
        print(f"\nORPHAN MESSAGES: {len(id_mismatches)} messages don't exist in the Registry.")
        # print("\n".join(id_mismatches[:10])) # Show first 10

if __name__ == "__main__":
    cross_reference_audit()
