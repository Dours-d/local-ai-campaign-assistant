import os
import re
import json

def main():
    messages_dir = "data/trustee_messages"
    log_path = "data/batch_run_new_trustees_v18.log"
    
    # 1. Extract slugs and their files
    msg_slugs = {} # slug -> [filenames]
    if os.path.exists(messages_dir):
        for f in os.listdir(messages_dir):
            if f.endswith(".txt"):
                path = os.path.join(messages_dir, f)
                try:
                    with open(path, 'r', encoding='utf-8') as mf:
                        content = mf.read()
                    slugs = re.findall(r'chuffed\.org/project/([\w-]+)', content)
                    for s in slugs:
                        if s not in msg_slugs: msg_slugs[s] = []
                        msg_slugs[s].append(f)
                except: pass
    
    print(f"Found {len(msg_slugs)} unique Chuffed slugs in messages.")
    if not msg_slugs:
        print("No slugs found. Mapping impossible via this route.")
        return

    # 2. Extract WhyDonate URLs from log
    wd_urls = {} # slug -> URL
    if os.path.exists(log_path):
        with open(log_path, 'r', encoding='utf-8', errors='ignore') as log_file:
            log_content = log_file.read()
            # Extract [SUCCESS] BID: URL
            successes = re.findall(r'\[SUCCESS\] \d+: (https://whydonate.com/fundraising/([\w-]+))', log_content)
            for url, slug in successes:
                wd_urls[slug] = url
    
    print(f"Found {len(wd_urls)} WhyDonate success URLs in log.")

    # 3. Match Chuffed Slugs to WhyDonate Slugs via Title/Content similarity
    # Since we don't have titles here, we'll use string coincidence between slugs
    updated_count = 0
    for c_slug, files in msg_slugs.items():
        # Heuristic matching
        best_wd_url = None
        for w_slug, url in wd_urls.items():
            # If chuffed slug is "help-aya" and whydonate is "help-aya-in-gaza", they match
            if c_slug in w_slug or w_slug in c_slug:
                best_wd_url = url
                break
        
        if best_wd_url:
            for f in files:
                print(f"MATCH: {c_slug} -> {f} -> {best_wd_url}")
                path = os.path.join(messages_dir, f)
                with open(path, 'r', encoding='utf-8') as rf:
                    content = rf.read()
                
                if best_wd_url in content: continue
                
                # Append or Replace
                if "[[LIVE_URL]]" in content:
                    new_content = content.replace("[[LIVE_URL]]", best_wd_url)
                else:
                    new_content = content + f"\n\nLive WhyDonate Campaign: {best_wd_url}"
                
                with open(path, 'w', encoding='utf-8') as wf:
                    wf.write(new_content)
                updated_count += 1

    print(f"Reconciliation complete. Updated {updated_count} message files.")

if __name__ == "__main__":
    main()
