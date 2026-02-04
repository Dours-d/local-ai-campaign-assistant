
import os
import json
import hashlib

exports_path = "data/exports"
text_ids = [
    "Please_brother_I_need_help",
    "Please_help_me_create_a_link_so_I_can_help_my_children",
    "Please_please_please_answer_me_"
]

# Map content to filenames
content_map = {}

for filename in os.listdir(exports_path):
    if filename.endswith(".json"):
        with open(os.path.join(exports_path, filename), 'r', encoding='utf-8') as f:
            try:
                content = f.read()
                if content not in content_map:
                    content_map[content] = []
                content_map[content].append(filename)
            except:
                continue

results = {}
for text_id in text_ids:
    target_file = text_id + ".json"
    target_path = os.path.join(exports_path, target_file)
    if not os.path.exists(target_path):
        continue
    
    with open(target_path, 'r', encoding='utf-8') as f:
        content = f.read()
        matches = content_map.get(content, [])
        # Find matches that are phone numbers
        numbers = [m.replace(".json", "") for m in matches if any(c.isdigit() for c in m)]
        results[text_id] = numbers

print(json.dumps(results, indent=2))
