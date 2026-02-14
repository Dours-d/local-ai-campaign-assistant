import os
import re
import json

# Paths
LOG_FILES = [
    "data/batch_run_v5_resume.log",
    "data/batch_run_new_trustees.log",
    "data/whydonate_creation_log.json",
    "data/whydonate_batch_create.json"
]
MESSAGES_DIR = "data/trustee_messages"
CAMPAIGNS_FILE = "data/campaigns_remaining.json"

def main():
    print("Starting Comprehensive Content-Based Reconciliation...", flush=True)

    # 1. Harvest ALL WhyDonate URLs from Logs
    wd_urls = {} # slug -> full_url
    
    for log_path in LOG_FILES:
        if not os.path.exists(log_path): continue
        print(f"Scanning {log_path}...", flush=True)
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Find all https://whydonate.com/fundraising/slug
                matches = re.findall(r'https://whydonate.com/fundraising/([\w-]+)', content)
                for slug in matches:
                    if slug in ['start', 'create', 'search']: continue
                    wd_urls[slug] = f"https://whydonate.com/fundraising/{slug}"
        except Exception as e:
             print(f"Error reading {log_path}: {e}")

    print(f"Found {len(wd_urls)} unique WhyDonate URLs.", flush=True)

    # 2. Map Chuffed IDs to Slugs (Heuristic & direct extraction if possible)
    # We need to know which Chuffed ID corresponds to which WhyDonate URL.
    # If the logs don't have "ID: URL" format, we rely on title matching/slug matching.
    
    # Let's load campaign data to help with matching
    chuffed_campaigns = []
    try:
        with open(CAMPAIGNS_FILE, 'r', encoding='utf-8') as f:
            chuffed_campaigns = json.load(f)
    except: pass
    
    # Map Chuffed ID -> WhyDonate URL based on Title <-> Slug matching
    bid_to_wd_url = {}
    
    for camp in chuffed_campaigns:
        bid = str(camp.get('bid'))
        title = camp.get('title', '').lower().replace(',', '').replace('.', '')
        
        # Check against all WD slugs
        best_match = None
        for slug, url in wd_urls.items():
            slug_parts = slug.split('-')
            match_count = sum(1 for p in slug_parts if p in title)
            if match_count >= len(slug_parts) * 0.6 and len(slug_parts) > 2:
                best_match = url
                break
        
        if best_match:
            bid_to_wd_url[bid] = best_match
            print(f"Mapped Chuffed ID {bid} -> {best_match}")

    # 3. Scan Message Files for Chuffed Links/IDs
    print("Scanning Message Files...", flush=True)
    updated_count = 0
    
    if os.path.exists(MESSAGES_DIR):
        for filename in os.listdir(MESSAGES_DIR):
            if not filename.endswith(".txt"): continue
            filepath = os.path.join(MESSAGES_DIR, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check if this file contains any of our mapped Chuffed IDs
                matched_bid = None
                
                # Check 1: Direct Chuffed ID presence (e.g. "126397")
                # We interpret the user's hint: "often the number into chuffed links... present into one's chat"
                for bid in bid_to_wd_url.keys():
                    if bid in content:
                        matched_bid = bid
                        break
                
                if matched_bid:
                    wd_url = bid_to_wd_url[matched_bid]
                    print(f"MATCH: File {filename} contains ID {matched_bid}. Updating with {wd_url}")
                    
                    # Avoid duplicates
                    if wd_url in content:
                        print(f"  Skipping {filename} - URL already present.")
                        continue

                    # Update Content
                    if "[[LIVE_URL]]" in content:
                        new_content = content.replace("[[LIVE_URL]]", wd_url)
                    elif "campaign link:" in content.lower():
                        new_content = re.sub(r"(campaign link:).*", f"\\1 {wd_url}", content, flags=re.IGNORECASE)
                    else:
                        new_content = content + f"\n\nLive WhyDonate Campaign: {wd_url}"
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    updated_count += 1
                    
            except Exception as e:
                print(f"Error processing {filename}: {e}")

    print(f"Reconciliation Complete. Updated {updated_count} files.")

if __name__ == "__main__":
    main()
