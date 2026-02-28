import json

with open('data/UNIFIED_REGISTRY.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for c in data:
    s = str(c.get('story', '')).strip()
    d = str(c.get('description', '')).strip()
    # Check if they are empty, or missing, or "empty"
    if not s or not d or s.lower() == 'empty' or d.lower() == 'empty':
        ident = c.get('identity_name') or c.get('bid')
        print(f"ID: {ident} | Story len {len(s)} | Desc len {len(d)}")
        
import glob
for fpath in glob.glob('data/submissions/*.json'):
    with open(fpath, 'r', encoding='utf-8') as f:
        c = json.load(f)
        s = str(c.get('story', '')).strip()
        d = str(c.get('description', '')).strip()
        if not s or not d or s.lower() == 'empty' or d.lower() == 'empty':
            ident = c.get('identity_name') or c.get('bid') or fpath
            print(f"SUBMISSION ID: {ident} | Story len {len(s)} | Desc len {len(d)}")
