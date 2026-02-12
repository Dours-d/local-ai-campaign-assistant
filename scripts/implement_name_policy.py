import json
import os
import re
from collections import Counter

DATA_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UNIFIED_PATH = os.path.join(DATA_DIR, "data", "campaigns_unified.json")

def implement_stable_name_policy():
    if not os.path.exists(UNIFIED_PATH):
        print("Error: unified database not found.")
        return

    with open(UNIFIED_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    campaigns = data.get("campaigns", [])
    
    # 1. Group by First Name
    name_groups = {}
    
    # helper to normalize names
    def get_fname(c):
        # MANUAL FIX: "The Ahmed" (Smile Campaign) was misidentified as "Lets"
        if c.get("id") == "chuffed_151256":
            return "Ahmed"

        privacy = c.get("privacy", {})
        val = privacy.get("first_name")
        full = privacy.get("full_name")
        display = privacy.get("display_name")
        
        # Basis for grouping
        basis = str(val or "").strip()
        if not basis or basis.lower() in ["unknown", "none", "null"]:
            basis = str(display or full or "Unknown").strip()
            
        parts = basis.split()
        if not parts: return "Unknown"
        
        standard_prefixes = ["umm", "um", "om", "abu", "aba", "abi", "bin", "bint"]
        
        # Logic: If the first word is a prefix, we ALWAYS want the second word too
        # This handles cases where people are called "Abu Ahmed" or "Umm Reem"
        primary_prefix = parts[0].lower()
        if primary_prefix in standard_prefixes:
            if len(parts) > 1:
                return f"{parts[0]} {parts[1]}"
            else:
                # If only one part (the prefix), try to find the full name context
                context_parts = str(full or display or "").strip().split()
                if len(context_parts) > 1 and context_parts[0].lower() == primary_prefix:
                    return f"{context_parts[0]} {context_parts[1]}"
                return parts[0] # Fallback to just "Abu" if nothing else exists
        
        # For non-prefix names, group by the first name part (e.g. "Ahmed")
        return parts[0]

    for c in campaigns:
        fname = get_fname(c)
        if fname not in name_groups:
            name_groups[fname] = []
        name_groups[fname].append(c)

    updates_count = 0
    
    # 2. Process each group
    for fname, group in name_groups.items():
        if fname == "Unknown":
            continue

        # Check existing internal_names to find used suffixes
        existing_suffixes = set()
        pending_assignment = []
        
        # Regex to capture "Name-###" pattern strictly
        pattern = re.compile(f"^{re.escape(fname)}-(\\d{{3}})$")

        for c in group:
            privacy = c.get("privacy", {})
            internal = privacy.get("internal_name")
            
            # Check if it has a valid existing ID
            match = pattern.match(internal) if internal else None
            
            if match:
                # This campaign already has a valid ID, lock it in.
                suffix_int = int(match.group(1))
                existing_suffixes.add(suffix_int)
                # Ensure homonym_suffix matches
                c["privacy"]["homonym_suffix"] = f"-{suffix_int:03d}"
            else:
                # Needs assignment (or simple name check)
                pending_assignment.append(c)

        # If we have no existing suffixes and only 1 campaign total, 
        # allows it to remain without suffix (unless we want strict policy everywhere)
        # POLICY DECISION: The user asked for differentiation for homonyms.
        # However, to be stable, if we later add a 2nd "Ahmed", the 1st "Ahmed" 
        # (which might be published as just "Ahmed") needs to stay "Ahmed" or become "Ahmed-001"?
        # Changing "Ahmed" to "Ahmed-001" breaks the link if the link was "Ahmed".
        # BUT: The user specifically requested "-###".
        # SAFE APPROACH: If count > 1 OR (count == 1 but we already have suffixed versions), force suffix.
        
        # FORCE SUFFIX for common prefixes (Abu, Umm, etc.) to ensure a "sustained" policy
        standard_prefixes = ["umm", "um", "om", "abu", "aba", "abi", "bin", "bint"]
        is_prefix_name = any(fname.lower().startswith(p + " ") for p in standard_prefixes) or fname.lower() in standard_prefixes
        
        should_suffix = len(group) > 1 or len(existing_suffixes) > 0 or is_prefix_name
        
        if not should_suffix:
            # Single unique name, no suffix needed.
            # Ensure it doesn't have a stale formatted name
            c = group[0]
            if "privacy" not in c: c["privacy"] = {}
            c["privacy"]["internal_name"] = fname
            c["privacy"]["homonym_suffix"] = None
            continue

        # Sort pending by created_at to be deterministic for new additions
        pending_assignment.sort(key=lambda x: (x.get("created_at") or "", x["id"]))
        
        # Determine next available suffix
        next_suffix = 1
        
        for c in pending_assignment:
            # Find next free slot
            while next_suffix in existing_suffixes:
                next_suffix += 1
            
            suffix_str = f"-{next_suffix:03d}"
            internal_name = f"{fname}{suffix_str}"
            
            if "privacy" not in c: c["privacy"] = {}
            
            old_name = c["privacy"].get("internal_name")
            if old_name != internal_name:
                print(f"Updating {old_name} -> {internal_name}")
                c["privacy"]["internal_name"] = internal_name
                c["privacy"]["homonym_suffix"] = suffix_str
                updates_count += 1
                
            existing_suffixes.add(next_suffix)

    # 3. Save updated database
    if updates_count > 0:
        with open(UNIFIED_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Database updated. {updates_count} new internal names assigned.")
    else:
        print("Database policy audit complete. No changes needed (Stable).")

    # 4. Verify uniqueness
    all_internals = []
    for c in campaigns:
        i = c.get("privacy", {}).get("internal_name")
        if i: all_internals.append(i)
    
    dupes = [item for item, count in Counter(all_internals).items() if count > 1]
    if dupes:
        print(f"WARNING: Duplicate internal names found: {dupes}")
    else:
        print("Integrity Check Passed: All internal names are unique.")

if __name__ == "__main__":
    implement_stable_name_policy()
