import os
import json
import re

def normalize(text):
    if not text: return ""
    return re.sub(r'[^a-zA-Z0-9]', '', str(text).lower())

def main():
    log_path = "data/whydonate_creation_log.json"
    index_path = "campaign_index_full.json"
    messages_dir = "data/trustee_messages"
    
    # 1. Harvest Title -> URL from Creation Log
    title_to_url = {}
    if os.path.exists(log_path):
        with open(log_path, 'r', encoding='utf-8') as f:
            log_data = json.load(f)
            for entry in log_data:
                url = entry.get('state', {}).get('url', '')
                if "/fundraising/" in url and not url.endswith("/start") and not url.endswith("/create") and not url.endswith("/dashboard"):
                    # Find the title in the inputs
                    title = None
                    for inp in entry.get('state', {}).get('inputs', []):
                        if inp.get('placeholder') == "Fundraiser Title":
                            title = inp.get('value')
                            break
                    
                    if not title:
                        # Fallback: find any non-empty input if title placeholder isn't there
                        # but usually it's there in Step 3/4
                        pass
                    
                    if title and url:
                        title_to_url[normalize(title)] = url

    print(f"Harvested {len(title_to_url)} Title -> URL pairs from creation log.")

    # 2. Load Index and Map URL to Phone
    phone_to_url = {}
    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            idx = json.load(f)
            for phone, info in idx.items():
                wd_title = info.get('whydonate', {}).get('title', '')
                norm_title = normalize(wd_title)
                if norm_title in title_to_url:
                    phone_to_url[phone.replace("+", "")] = title_to_url[norm_title]
                else:
                    # Try partial match or BID match
                    bid = info.get('chuffed', {}).get('id')
                    # If log has BID-Title mapping elsewhere or if we use the automation log
                    pass

    print(f"Mapped {len(phone_to_url)} WhyDonate URLs to Phone Numbers.")

    # 3. Update Message Files
    updated = 0
    if os.path.exists(messages_dir):
        for phone, url in phone_to_url.items():
            target_msg = None
            for mf in os.listdir(messages_dir):
                if phone in mf and mf.endswith(".txt"):
                    target_msg = mf
                    break
            
            if target_msg:
                path = os.path.join(messages_dir, target_msg)
                with open(path, 'r', encoding='utf-8') as rf:
                    content = rf.read()
                
                if url not in content:
                    print(f"UPDATING: {target_msg} -> {url}")
                    if "[[LIVE_URL]]" in content:
                        new_content = content.replace(" [[LIVE_URL]]", f" {url}").replace("[[LIVE_URL]]", url)
                    else:
                        new_content = content + f"\n\nLive WhyDonate Campaign: {url}"
                    
                    with open(path, 'w', encoding='utf-8') as wf:
                        wf.write(new_content)
                    updated += 1
    
    print(f"Reconciliation complete. Updated {updated} message files.")

if __name__ == "__main__":
    main()
