import json
import os
import re

def filter_real_growth_list():
    base_dir = r"c:\Users\gaelf\Documents\GitHub\local_ai_campaign_assistant"
    report_path = os.path.join(base_dir, "data", "potential_campaigns_report.md")
    validated_path = os.path.join(base_dir, "data", "validated_ghost_contacts.json")
    final_output_path = os.path.join(base_dir, "data", "final_real_growth_list.md")
    final_json_path = os.path.join(base_dir, "data", "final_real_growth_list.json")

    # 1. Extract IDs from the potential_campaigns_report.md
    with open(report_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # IDs are in markdown tables, looking for digits or strings starting with 1
    potential_ids = re.findall(r"\|\s+(\d+|viral_\w+)\s+\|", content)
    unique_potential_ids = set(potential_ids)

    # 2. Load validated contacts
    with open(validated_path, "r", encoding="utf-8") as f:
        validated_data = json.load(f)

    # 3. Filter
    real_missions = []
    skipped_missions = []

    # Map validated data by bid for easy lookup
    # Normalize bid to string and handle "chuffed_" prefix
    validated_map = {item["bid"]: item for item in validated_data}

    for pid in unique_potential_ids:
        # Check both direct and with chuffed_ prefix
        lookup_key = pid if pid.startswith("viral_") else f"chuffed_{pid}"
        if lookup_key in validated_map:
            real_missions.append(validated_map[lookup_key])
        else:
            skipped_missions.append(pid)

    # 4. Write Final Report
    with open(final_output_path, "w", encoding="utf-8") as f:
        f.write("# 🏆 Final Real Growth List\n\n")
        f.write(f"This list contains only the potential campaigns from the ghost recovery effort that have a **confirmed WhatsApp contact**. These are the only ones ready for manual creation.\n\n")
        f.write(f"- Total Potential Candidates: {len(unique_potential_ids)}\n")
        f.write(f"- Validated with Contact: {len(real_missions)}\n")
        f.write(f"- Dropped (No Contact): {len(skipped_missions)}\n\n")
        
        f.write("## ✅ Verified for Manual Creation\n")
        f.write("| WhatsApp | Chuffed ID | Title | Source |\n")
        f.write("|----------|------------|-------|--------|\n")
        for m in sorted(real_missions, key=lambda x: str(x.get('whatsapp'))):
            whatsapp = m.get('whatsapp', 'MISSING')
            bid = m.get('bid', 'N/A')
            title = m.get('title', 'N/A')[:50] + "..."
            source = m.get('validation_source', 'N/A')
            f.write(f"| {whatsapp} | {bid} | {title} | {source} |\n")

        f.write("\n## ❌ Dropped (Missing WhatsApp Anchor)\n")
        for s in sorted(skipped_missions):
            f.write(f"- {s}\n")

    # 5. Write JSON for automation
    with open(final_json_path, "w", encoding="utf-8") as f:
        json.dump(real_missions, f, indent=4)

    print(f"Final filtering complete. Real: {len(real_missions)}, Dropped: {len(skipped_missions)}")

if __name__ == "__main__":
    filter_real_growth_list()
