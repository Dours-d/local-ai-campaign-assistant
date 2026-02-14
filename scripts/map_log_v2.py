import re
import os
import json

def main():
    log_path = "data/batch_run_new_trustees_v18.log"
    if not os.path.exists(log_path):
        print("Log not found.")
        return

    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    mappings = [] # List of {bid, phone, url}
    current_bid = None
    current_phone = None
    
    for line in lines:
        # Detect BID start (from process_item: print(f"--- {item['bid']} ---"))
        # Or from navigation: [SUCCESS] BID: URL
        bid_header = re.search(r'--- (\d+) ---', line)
        if bid_header:
            current_bid = bid_header.group(1)
            current_phone = None # Reset phone when new BID starts
        
        # Detect Phone from screenshots
        phone_match = re.search(r'verify_s\d_(\d+)\.png', line)
        if phone_match:
            current_phone = phone_match.group(1)
        
        # Detect Success
        success_match = re.search(r'\[SUCCESS\] (\d+): (https://whydonate.com/fundraising/[\w-]+)', line)
        if success_match:
            bid = success_match.group(1)
            url = success_match.group(2)
            mappings.append({
                "bid": bid,
                "phone": current_phone,
                "url": url
            })
            print(f"MAPPED: BID {bid} -> Phone {current_phone} -> URL {url}")

    print(f"\nTotal mappings: {len(mappings)}")
    
    # Save results
    with open('data/reconciliation_map_v2.json', 'w', encoding='utf-8') as f:
        json.dump(mappings, f, indent=2)

if __name__ == "__main__":
    main()
