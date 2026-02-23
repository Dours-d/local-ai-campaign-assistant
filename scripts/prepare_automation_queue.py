import json
import os
import re

GROWTH_LIST_PATH = "data/final_real_growth_list.json"
OUTPUT_QUEUE_PATH = "data/final_automation_queue.json"

def resolve_identity(camp):
    # Priority 1: Registry Name (The "Definite Choice")
    if camp.get("registry_name"):
        return camp["registry_name"]
    
    # Priority 2: Word Toggles (Scarcity Resolution)
    title = camp.get("title", "")
    indices = camp.get("identity_indices", [0, 1])
    words = title.split()
    if words:
        # Filter out numbers and special chars for the name
        selected = [words[i] for i in indices if i < len(words)]
        name = " ".join(selected)
        name = re.sub(r'[^\w\s]', '', name)
        if name.strip(): return name
        
    return "Trustee" # Ultimate fallback

def prepare_queue():
    if not os.path.exists(GROWTH_LIST_PATH):
        print(f"Error: {GROWTH_LIST_PATH} not found.")
        return

    with open(GROWTH_LIST_PATH, 'r', encoding='utf-8') as f:
        growth_list = json.load(f)

    queue = []
    print(f"Preparing Queue from {len(growth_list)} items...")

    for camp in growth_list:
        if camp.get("status") == "completed": continue
        
        identity = resolve_identity(camp)
        
        # Clean title for WhyDonate (limit length)
        title = camp.get("title", "Support Campaign")[:70]
        
        entry = {
            "bid": camp.get("bid"),
            "beneficiary_name": identity,
            "title": title,
            "campaign_description": camp.get("description", "Please help this family in Gaza."),
            "goal": camp.get("goal", 5000),
            "image": camp.get("image", "")
        }
        queue.append(entry)
        print(f"Queued: {camp.get('bid')} -> Identity: {identity}")

    with open(OUTPUT_QUEUE_PATH, 'w', encoding='utf-8') as f:
        json.dump(queue, f, ensure_ascii=False, indent=4)

    print(f"\nFinal Automation Queue saved to {OUTPUT_QUEUE_PATH}")
    print(f"Ready to run: python scripts/whydonate_batch_automater.py {OUTPUT_QUEUE_PATH}")

if __name__ == "__main__":
    prepare_queue()
