import json
import glob
import os

PLACEHOLDER_TEXT = "We are the natural owners of our time and our solidarity. Join us in preserving life and dignity."

def update_empty_story(filepath):
    if not os.path.exists(filepath):
        return 0

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return 0

    updates = 0
    
    if isinstance(data, list):
        for item in data:
            story = item.get('story', '')
            if not story or not str(story).strip():
                item['story'] = PLACEHOLDER_TEXT
                updates += 1
    elif isinstance(data, dict):
        story = data.get('story', '')
        if not story or not str(story).strip():
            data['story'] = PLACEHOLDER_TEXT
            updates += 1

    if updates > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
    return updates

total_updates = 0

# Check UNIFIED_REGISTRY
updates = update_empty_story('data/UNIFIED_REGISTRY.json')
total_updates += updates
print(f"Updated {updates} campaigns in UNIFIED_REGISTRY.json")

# Check batch_queue
updates = update_empty_story('data/batch_queue.json')
total_updates += updates
print(f"Updated {updates} campaigns in batch_queue.json")

# Check final_real_growth_list
updates = update_empty_story('data/final_real_growth_list.json')
total_updates += updates
print(f"Updated {updates} campaigns in final_real_growth_list.json")

# Check submissions
for fpath in glob.glob('data/submissions/*.json'):
    updates = update_empty_story(fpath)
    total_updates += updates

print(f"Total empty descriptions populated with placeholder: {total_updates}")
