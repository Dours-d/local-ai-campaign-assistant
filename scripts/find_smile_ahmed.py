import json

def find_ahmed():
    with open('data/campaigns_unified.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    for c in data.get('campaigns', []):
        title = c.get('title', '')
        if 'smile' in title.lower():
            internal_name = c['privacy'].get('internal_name', 'N/A')
            print(f"ID: {c['id']}")
            print(f"Internal Name: {internal_name}")
            print(f"Title: {title}")
            print("-" * 20)

if __name__ == "__main__":
    find_ahmed()
