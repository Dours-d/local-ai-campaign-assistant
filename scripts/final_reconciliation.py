import os
import json
import re

def main():
    log_path = "data/batch_run_new_trustees_v18.log"
    index_path = "campaign_index_full.json"
    messages_dir = "data/trustee_messages"
    
    # 1. Load Phone -> BID Mapping
    phone_to_bid = {} # BID -> Phone
    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            idx = json.load(f)
            for phone, info in idx.items():
                bid = info.get('chuffed', {}).get('id')
                if bid:
                    phone_to_bid[bid] = phone.replace("+", "") # Strip + for matching
    
    print(f"Loaded {len(phone_to_bid)} phone-to-BID mappings from index.")

    # 2. Load BID -> WhyDonate Mapping from Log
    bid_to_url = {}
    if os.path.exists(log_path):
        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            # [SUCCESS] BID: URL
            matches = re.findall(r'\[SUCCESS\] (\d+): (https://whydonate.com/fundraising/[\w-]+)', content)
            for bid, url in matches:
                bid_to_url[bid] = url
    
    print(f"Found {len(bid_to_url)} success URLs in log.")

    # 3. Perform Reconciliation
    updates = []
    for bid, url in bid_to_url.items():
        phone = phone_to_bid.get(bid)
        if phone:
            # Match phone to message file
            # Filenames are like "+972592645759_status_update.txt" or "972592645759_status_update.txt"
            target_msg = None
            for mf in os.listdir(messages_dir):
                if phone in mf and mf.endswith(".txt"):
                    target_msg = mf
                    break
            
            if target_msg:
                msg_path = os.path.join(messages_dir, target_msg)
                print(f"UPDATING: {target_msg} for BID {bid} -> {url}")
                with open(msg_path, 'r', encoding='utf-8') as f:
                    m_content = f.read()
                
                if url not in m_content:
                    if "[[LIVE_URL]]" in m_content:
                        new_content = m_content.replace(" [[LIVE_URL]]", f" {url}").replace("[[LIVE_URL]]", url)
                    else:
                        new_content = m_content + f"\n\nLive Campaign URL: {url}"
                    
                    with open(msg_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    updates.append(target_msg)
            else:
                print(f"WARNING: No message file found for phone {phone} (BID {bid})")
        else:
            print(f"WARNING: No phone mapping found for BID {bid}")

    print(f"Reconciliation finished. Updated {len(updates)} message files.")

if __name__ == "__main__":
    main()
