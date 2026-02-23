import json
import re
import os

def normalize(phone):
    if not phone: return ""
    return re.sub(r'\D', '', str(phone))

def unify_truth_layer():
    # 1. Load existing registry
    with open('campaign_index_full.json', 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    # 2. Load recovery data
    with open('data/orphan_recovery.json', 'r', encoding='utf-8') as f:
        recovery = json.load(f)
        
    unified_registry = {}
    
    # Normalize existing registry
    for phone, data in registry.items():
        norm_phone = normalize(phone)
        # Store with normalized key (standardizing on no '+')
        unified_registry[norm_phone] = data
        # Ensure beneficiary_id is also normalized if present
        if data.get('beneficiary_id'):
            data['beneficiary_id'] = normalize(data['beneficiary_id'])
            
    # Merge recovery data
    merged_count = 0
    for orphan_id, data in recovery.items():
        norm_id = normalize(orphan_id)
        if norm_id not in unified_registry:
            # Create a basic entry for recovered orphans
            unified_registry[norm_id] = {
                "beneficiary_id": norm_id,
                "whatsapp_normalized": data.get('whatsapp'),
                "recovery_source": data.get('source'),
                "whydonate": {
                    "status": "pending_individual_creation",
                    "temp_link": "https://dours-d.github.io/local-ai-campaign-assistant/"
                }
            }
            merged_count += 1
            
    # 3. Save Unified Registry
    with open('campaign_index_full.json', 'w', encoding='utf-8') as f:
        json.dump(unified_registry, f, indent=2)
        
    print(f"UNIFICATION COMPLETE:")
    print(f"  - Total entries in Registry: {len(unified_registry)}")
    print(f"  - Merged Orphans: {merged_count}")
    print(f"  - Formatting: All keys normalized (digits only).")

if __name__ == "__main__":
    unify_truth_layer()
