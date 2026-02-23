import os

OUTBOX_DIR = "data/onboarding_outbox"
OUTPUT_FILE = "onboarding_messages.txt"

def consolidate():
    if not os.path.exists(OUTBOX_DIR):
        print(f"Outbox {OUTBOX_DIR} not found.")
        return
    
    all_files = os.listdir(OUTBOX_DIR)
    campaign_files = {f.split("_campaign.txt")[0]: f for f in all_files if f.endswith("_campaign.txt")}
    onboarding_files = {f.split("_onboarding.txt")[0]: f for f in all_files if f.endswith("_onboarding.txt")}
    
    # Combine BIDs, prioritizing campaigns
    all_bids = sorted(list(set(campaign_files.keys()) | set(onboarding_files.keys())))
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        for bid in all_bids:
            if bid in campaign_files:
                filename = campaign_files[bid]
            else:
                filename = onboarding_files[bid]
                
            with open(os.path.join(OUTBOX_DIR, filename), "r", encoding="utf-8") as f:
                content = f.read()
            
            out.write(f"--- MESSAGE FOR {bid} ---\n")
            out.write(content)
            out.write("\n" + "-"*30 + "\n\n")
            
    print(f"Consolidated {len(all_bids)} messages into {OUTPUT_FILE}")

if __name__ == "__main__":
    consolidate()
