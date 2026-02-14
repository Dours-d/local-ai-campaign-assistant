import os
import json
import re

def main():
    print("Starting verification & reconciliation...", flush=True)
    
    # 1. Load Campaign Unified
    try:
        with open('data/campaigns_unified.json', 'r', encoding='utf-8') as f:
            unified = json.load(f)
    except Exception as e:
        print(f"Error loading campaigns_unified.json: {e}")
        return

    # 2. Extract Valid URLs from creation log
    valid_urls = {}
    try:
        with open('data/whydonate_creation_log.json', 'r', encoding='utf-8') as f:
            log_content = f.read()
            # Regex to find URLs
            urls = re.findall(r'https://whydonate.com/fundraising/([\w-]+)', log_content)
            for slug in urls:
                if slug in ['start', 'create', 'search']: continue
                valid_urls[slug] = f"https://whydonate.com/fundraising/{slug}"
    except Exception as e:
        print(f"Error reading whydonate_creation_log.json: {e}")

    # Also check batch_run_v5_resume.log for success lines if any
    try:
        if os.path.exists('data/batch_run_v5_resume.log'):
            with open('data/batch_run_v5_resume.log', 'r', encoding='utf-8') as f:
                for line in f:
                    if "fundraising/" in line and "SUCCESS" in line:
                         match = re.search(r'https://whydonate.com/fundraising/([\w-]+)', line)
                         if match:
                             slug = match.group(1)
                             valid_urls[slug] = f"https://whydonate.com/fundraising/{slug}"
    except: pass
    
    print(f"Found {len(valid_urls)} valid URL candidates: {list(valid_urls.keys())}")
    
    # 3. Map Slugs to Campaigns
    count_updated = 0
    for camp in unified.get('campaigns', []):
        title = camp.get('title', '').replace(',', '').replace('.', '').lower()
        internal_name = camp.get('privacy', {}).get('internal_name')
        if not internal_name: continue
        
        # Heuristic matching
        matched_url = None
        for slug, url in valid_urls.items():
            slug_parts = slug.split('-')
            # Check if significant parts of slug are in title
            matches = sum(1 for p in slug_parts if p in title)
            if matches >= len(slug_parts) * 0.6 and len(slug_parts) > 2:
                matched_url = url
                break
        
        if matched_url:
            print(f"MATCH: {internal_name} -> {matched_url}")
            
            # 4. Update Message File
            found_msg = False
            if not os.path.exists('data/trustee_messages'): continue
            
            for msg_file in os.listdir('data/trustee_messages'):
                if not msg_file.endswith('.txt'): continue
                path = os.path.join('data/trustee_messages', msg_file)
                try:
                    with open(path, 'r', encoding='utf-8') as mf:
                        content = mf.read()
                    
                    # Check if First Name is in content (e.g. "Aya" in "Hi Aya, ...")
                    first_name = internal_name.split('-')[0]
                    if first_name in content:
                        print(f"  Found matching message file: {msg_file}")
                        
                        # Avoid duplicates
                        if matched_url in content:
                            print("  URL already present.")
                            found_msg = True
                            break
                        
                        # Replace or Append
                        if "[[LIVE_URL]]" in content:
                            new_content = content.replace("[[LIVE_URL]]", matched_url)
                        elif "campaign link:" in content.lower():
                            new_content = re.sub(r"(campaign link:).*", f"\\1 {matched_url}", content, flags=re.IGNORECASE)
                        else:
                            new_content = content + f"\n\nLive WhyDonate Campaign: {matched_url}"
                        
                        with open(path, 'w', encoding='utf-8') as wf:
                            wf.write(new_content)
                        print("  Updated.")
                        count_updated += 1
                        found_msg = True
                        break
                except: pass
            
            if not found_msg:
                print(f"  Warning: No matching message file found for {internal_name} ({first_name})")

    print(f"Reconciliation complete. Updated {count_updated} messages.")

if __name__ == "__main__":
    main()
