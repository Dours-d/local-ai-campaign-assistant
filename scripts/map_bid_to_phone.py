import re
import json
import os

def main():
    log_path = "data/batch_run_new_trustees_v18.log"
    if not os.path.exists(log_path):
        print("Log file not found.")
        return

    print(f"Analyzing {log_path} for BID/Phone proximity...", flush=True)
    
    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    mappings = {} # BID -> Phone
    current_bid = None
    
    for line in lines:
        # Look for BID
        bid_match = re.search(r'BID: (\d+)', line)
        if bid_match:
            current_bid = bid_match.group(1)
        
        # Look for phone in screenshot name
        # Format: verify_s1_972592475288.png
        phone_match = re.search(r'verify_s\d_(\d+)\.png', line)
        if phone_match and current_bid:
            phone = phone_match.group(1)
            mappings[current_bid] = phone
            # We don't reset current_bid yet because one BID might have multiple screenshots
    
    print(f"Found {len(mappings)} BID -> Phone mappings.")
    for b, p in list(mappings.items())[:10]:
        print(f"  {b} -> {p}")

    # Now let's find the WhyDonate URLs for these BIDs
    # Success lines often look like [SUCCESS] URL
    # We need to link them too.
    
    bid_to_url = {}
    current_bid = None
    for line in lines:
        bid_match = re.search(r'BID: (\d+)', line)
        if bid_match:
            current_bid = bid_match.group(1)
        
        # Look for WhyDonate URL and SUCCESS
        # Wait, how does the success line look? 
        # From previous steps: "Found 23 URLs in log" using https://whydonate.com/fundraising/[\w-]+
        if "SUCCESS" in line or "fundraising/" in line:
            url_match = re.search(r'https://whydonate.com/fundraising/([\w-]+)', line)
            if url_match and current_bid:
                slug = url_match.group(1)
                if slug not in ['start', 'create', 'search']:
                    bid_to_url[current_bid] = f"https://whydonate.com/fundraising/{slug}"

    print(f"Found {len(bid_to_url)} BID -> URL mappings.")

    # Combine everything
    final_reconciliation = {} # Phone -> URL
    for b, p in mappings.items():
        if b in bid_to_url:
            final_reconciliation[p] = bid_to_url[b]

    print(f"Final Reconciliation: {len(final_reconciliation)} Phone -> URL mappings.")
    with open('data/reconciliation_final.json', 'w', encoding='utf-8') as f:
        json.dump(final_reconciliation, f, indent=2)

if __name__ == "__main__":
    main()
