import os
import json
import glob

SUBMISSIONS_DIR = "data/onboarding_submissions"
BATCH_QUEUE_FILE = "data/batch_queue.json"
REGISTRY_FILE = "data/campaign_registry.json"

def prepare_batch():
    # Load registry to avoid re-provisioning
    registry_bids = set()
    if os.path.exists(REGISTRY_FILE):
        with open(REGISTRY_FILE, 'r', encoding='utf-8') as f:
            mappings = json.load(f).get("mappings", {})
            for bid, data in mappings.items():
                if data.get('whydonate_url'):
                    registry_bids.add(bid)

    queue = []
    submission_files = glob.glob(os.path.join(SUBMISSIONS_DIR, "*.json"))

    for sub_file in submission_files:
        if "test_ping" in sub_file or "MOCK-USER" in sub_file:
            continue
            
        try:
            with open(sub_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            bid_raw = data.get("beneficiary_id")
            if not bid_raw: continue
            
            # Clean BID (remove viral_+ if present)
            bid = bid_raw.replace("viral_+", "")
            
            if bid in registry_bids:
                print(f"Skipping {bid}: Already in registry.")
                continue

            # Validation: Must have title, story, and at least one image
            title = data.get("title")
            story = data.get("story")
            files = data.get("files", [])
            image_path = None
            for f in files:
                if f.get("path") and (".jpg" in f["path"].lower() or ".png" in f["path"].lower()):
                    # Convert to absolute path if relative
                    img_abs = os.path.abspath(f["path"])
                    if os.path.exists(img_abs):
                        image_path = img_abs
                        break
            
            if title and story and image_path:
                queue.append({
                    "bid": bid,
                    "title": title,
                    "description": story,
                    "goal": 5000, # Default goal
                    "image": image_path
                })
                print(f"Staging {bid} for batch.")
            else:
                print(f"Skipping {bid}: Incomplete data (Title/Story/Image).")

        except Exception as e:
            print(f"Error processing {sub_file}: {e}")

    with open(BATCH_QUEUE_FILE, 'w', encoding='utf-8') as f:
        json.dump(queue, f, indent=2)
    
    print(f"\nCreated {BATCH_QUEUE_FILE} with {len(queue)} items.")

if __name__ == "__main__":
    prepare_batch()
