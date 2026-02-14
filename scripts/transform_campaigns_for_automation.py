import json
import sys
import io

# Configure UTF-8 encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Load campaigns to create
with open('data/campaigns_to_create_final.json', 'r', encoding='utf-8') as f:
    campaigns = json.load(f)

print(f"Loaded {len(campaigns)} campaigns")

# Transform to automation format
transformed = []
for campaign in campaigns:
    # Create automation-compatible format
    auto_campaign = {
        "bid": str(campaign.get('chuffed_id') or campaign.get('id', 'unknown')),
        "title": campaign.get('title', 'Untitled Campaign'),
        "description": campaign.get('description') or f"Help support this campaign. Original goal: €{campaign.get('raised_eur', 0)}",
        "goal": campaign.get('goal') or campaign.get('raised_eur') or 5000,
        "image": campaign.get('image', '')
    }
    transformed.append(auto_campaign)

print(f"Transformed {len(transformed)} campaigns")

# Save transformed campaigns
with open('data/campaigns_automation_format.json', 'w', encoding='utf-8') as f:
    json.dump(transformed, f, ensure_ascii=False, indent=2)

print(f"Saved to data/campaigns_automation_format.json")
print(f"\nReady for batch creation!")
