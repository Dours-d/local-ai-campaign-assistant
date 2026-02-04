
import json
import collections
try:
    with open('data/launchgood_batch_create.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    stats = collections.Counter(c.get('status') for c in data)
    print(dict(stats))
except Exception as e:
    print(f"Error: {e}")
