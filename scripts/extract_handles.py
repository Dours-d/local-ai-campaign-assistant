import json
import os
import re

# Configuration
ACTIVE_ROOT = os.getcwd()
REGISTRY_PATH = os.path.join(ACTIVE_ROOT, 'vault', 'UNIFIED_REGISTRY.json')
OUTPUT_PATH = os.path.join(ACTIVE_ROOT, 'scripts', 'outreach_handles.txt')

def extract_handles():
    print(f"🔍 Scanning registry: {REGISTRY_PATH}")
    if not os.path.exists(REGISTRY_PATH):
        print(f"❌ Registry not found: {REGISTRY_PATH}")
        return

    with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    handles = set()
    # Simple regex for X handles
    handle_pattern = re.compile(r'@([a-zA-Z0-9_]{1,15})')

    # Deep scan across all fields in the registry
    def scan_obj(obj):
        if isinstance(obj, str):
            matches = handle_pattern.findall(obj)
            for m in matches:
                handles.add(m.lower())
        elif isinstance(obj, list):
            for item in obj:
                scan_obj(item)
        elif isinstance(obj, dict):
            for val in obj.values():
                scan_obj(val)

    scan_obj(data)

    # Sort and save
    sorted_handles = sorted(list(handles))
    if not os.path.exists(os.path.dirname(OUTPUT_PATH)):
        os.makedirs(os.path.dirname(OUTPUT_PATH))
        
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        for h in sorted_handles:
            f.write(f"@{h}\n")
    
    print(f"✅ Extracted {len(sorted_handles)} unique handles to {OUTPUT_PATH}")

if __name__ == "__main__":
    extract_handles()
