import json
import csv
import os

def validate_contacts():
    # Paths
    base_dir = r"c:\Users\gaelf\Documents\GitHub\local_ai_campaign_assistant"
    batch_queue_path = os.path.join(base_dir, "data", "batch_queue.json")
    couplings_path = os.path.join(base_dir, "data", "user_manual_couplings.json")
    report_path = os.path.join(base_dir, "data", "validated_ghost_contacts.json")
    md_report_path = os.path.join(base_dir, "data", "ghost_validation_summary.md")

    # Load data
    with open(batch_queue_path, "r", encoding="utf-8") as f:
        batch_queue = json.load(f)
    
    with open(couplings_path, "r", encoding="utf-8") as f:
        couplings = json.load(f)

    validated = []
    missing = []
    already_numbered = []

    for item in batch_queue:
        bid = item.get("bid", "")
        title = item.get("title", "").strip()
        
        # Case 1: Already a phone number
        if bid.isdigit() or (bid.startswith("+") and bid[1:].isdigit()):
            item["whatsapp"] = bid
            item["validation_source"] = "direct_bid"
            already_numbered.append(item)
            validated.append(item)
            continue
        
        # Case 2: Chuffed ID, lookup by title
        # Normalize title for better matching
        clean_title = title.replace("\u00a0", " ").strip()
        
        found_number = None
        for c_title, c_num in couplings.items():
            if clean_title.lower() in c_title.lower() or c_title.lower() in clean_title.lower():
                found_number = c_num
                break
        
        if found_number:
            item["whatsapp"] = found_number
            item["validation_source"] = "user_manual_couplings"
            validated.append(item)
        else:
            item["whatsapp"] = "MISSING"
            item["validation_source"] = "none"
            missing.append(item)

    # Write JSON report
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(validated, f, indent=4)

    # Write Markdown Summary
    with open(md_report_path, "w", encoding="utf-8") as f:
        f.write("# Ghost Validation Summary\n\n")
        f.write(f"Total Candidates: {len(batch_queue)}\n")
        f.write(f"- Already Numbered: {len(already_numbered)}\n")
        f.write(f"- Validated via Coupling: {len(validated) - len(already_numbered)}\n")
        f.write(f"- Still Missing: {len(missing)}\n\n")
        
        f.write("## Still Missing Numbers (Ghosts to Drop)\n")
        for m in missing:
            f.write(f"- [{m['bid']}] {m['title']}\n")
        
        f.write("\n## Validated Queue (Ready for Creation)\n")
        for v in validated:
            status = " [NEW]" if v['validation_source'] == 'user_manual_couplings' else " [LIVE]"
            f.write(f"- {status} {v['whatsapp']} | {v['title']} ({v['bid']})\n")

    print(f"Validation complete. Validated: {len(validated)}, Missing: {len(missing)}")

if __name__ == "__main__":
    validate_contacts()
