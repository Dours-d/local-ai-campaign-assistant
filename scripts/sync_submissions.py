import os
import json
import re

DATA_DIR = "data/onboarding_submissions"
GROWTH_LIST_PATH = "data/final_real_growth_list.json"
REGISTRY_PATH = "data/campaign_registry.json"

def clean_phone(phone):
    if not phone: return ""
    return "".join([c for c in str(phone) if c.isdigit()])

def run_sync():
    print("Starting Submission Sync...")
    
    # Load Registry
    registry = {}
    if os.path.exists(REGISTRY_PATH):
        with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
            reg_data = json.load(f).get("mappings", {})
            for k, v in reg_data.items():
                num = clean_phone(v.get("whatsapp") or k)
                if num:
                    registry[num] = v.get("name")
    
    # Load Current Growth List
    current_list = []
    if os.path.exists(GROWTH_LIST_PATH):
        with open(GROWTH_LIST_PATH, 'r', encoding='utf-8') as f:
            current_list = json.load(f)
    
    existing_nums = {clean_phone(c.get("whatsapp")) for c in current_list if c.get("whatsapp")}
    
    new_entries = []
    
    # Process Submissions
    for filename in os.listdir(DATA_DIR):
        if not filename.endswith("_submission.json"): continue
        
        path = os.path.join(DATA_DIR, filename)
        with open(path, 'r', encoding='utf-8') as f:
            sub = json.load(f)
            
            # Extract Phone
            raw_phone = sub.get("whatsapp_number")
            if not raw_phone and "viral_" in filename:
                # Try to extract from filename: viral_+972592645759_submission.json
                match = re.search(r'viral_\+?(\d+)', filename)
                if match: raw_phone = match.group(1)
            
            clean_wa = clean_phone(raw_phone)
            if not clean_wa:
                # Fallback to beneficiary_id if it looks like a number
                if sub.get("beneficiary_id", "").isdigit():
                    clean_wa = sub["beneficiary_id"]
            
            if not clean_wa or clean_wa in existing_nums:
                continue
            
            # Map to Registry (The "Identifier Line" merge)
            reg_name = registry.get(clean_wa)
            
            # Create Entry
            entry = {
                "bid": f"sub_{clean_wa}",
                "title": sub.get("title", "Untitled Campaign"),
                "description": sub.get("story", ""),
                "whatsapp": clean_wa,
                "goal": 5000,
                "status": "pending",
                "validation_source": "onboarding_submission",
                "registry_name": reg_name,
                "identity_indices": [0, 1] # Default to first two words
            }
            
            # Attach Image if available
            if sub.get("files") and len(sub["files"]) > 0:
                # Use absolute path for the manager to resolve correctly
                entry["image"] = os.path.abspath(sub["files"][0]["path"])
            
            new_entries.append(entry)
            existing_nums.add(clean_wa)
            print(f"Added: {clean_wa} ({reg_name or 'No Registry Match'})")

    # Save
    final_list = current_list + new_entries
    with open(GROWTH_LIST_PATH, 'w', encoding='utf-8') as f:
        json.dump(final_list, f, indent=4)
    
    print(f"Sync Complete! Added {len(new_entries)} new campaigns.")

if __name__ == "__main__":
    run_sync()
