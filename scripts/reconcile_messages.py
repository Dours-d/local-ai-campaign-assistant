import json
import os
import re

# Paths
LOG_FILE = "data/batch_run_v5_resume.log"
BENEFICIARIES_FILE = "data/potential_beneficiaries.json"
MESSAGES_DIR = "data/trustee_messages"

def main():
    print("Starting reconciliation...")
    
    # 1. Load Mappings
    if not os.path.exists(BENEFICIARIES_FILE):
        print(f"Error: {BENEFICIARIES_FILE} not found.")
        return
    
    with open(BENEFICIARIES_FILE, 'r', encoding='utf-8') as f:
        beneficiaries = json.load(f)
    
    # Create bid -> whatsapp_id mapping
    bid_to_whatsapp = {}
    for key, data in beneficiaries.items():
        bid = data.get('chuffed_id')
        whatsapp = data.get('whatsapp_id')
        if bid and whatsapp:
            bid_to_whatsapp[str(bid)] = str(whatsapp)
    
    # 2. Extract Successes from Log
    successes = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                if "[SUCCESS]" in line:
                    match = re.search(r"\[SUCCESS\] (\d+): (https://whydonate.com/fundraising/[\w-]+)", line)
                    if match:
                        bid = match.group(1)
                        url = match.group(2)
                        successes.append((bid, url))
    
    print(f"Found {len(successes)} successes in log.")
    
    # 3. Update Messages
    updated_count = 0
    for bid, url in successes:
        whatsapp = bid_to_whatsapp.get(bid)
        if not whatsapp:
            print(f"Warning: No WhatsApp mapping for bid {bid}")
            continue
        
        # Look for the message file
        # The files are named like +972..._status_update.txt or 972..._status_update.txt
        message_file = None
        for filename in os.listdir(MESSAGES_DIR):
            if filename.startswith(f"+{whatsapp}") or filename.startswith(whatsapp):
                if "_status_update.txt" in filename:
                    message_file = os.path.join(MESSAGES_DIR, filename)
                    break
        
        if message_file:
            print(f"Updating {message_file} with {url}")
            with open(message_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace placeholder or append
            if "[[LIVE_URL]]" in content:
                new_content = content.replace("[[LIVE_URL]]", url)
            elif "campaign link:" in content.lower():
                new_content = re.sub(r"(campaign link:)\s*.*", f"\\1 {url}", content, flags=re.IGNORECASE)
            else:
                new_content = content + f"\n\nLive WhyDonate Campaign: {url}"
            
            with open(message_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            updated_count += 1
        else:
            print(f"Warning: No message file found for WhatsApp {whatsapp} (bid {bid})")

    print(f"Update complete. {updated_count} messages updated.")

if __name__ == "__main__":
    main()
