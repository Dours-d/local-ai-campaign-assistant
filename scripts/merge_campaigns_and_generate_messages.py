import json
import sys
import io
from pathlib import Path

# Configure UTF-8 encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Load all campaign data
with open('data/whydonate_migration_pending.json', 'r', encoding='utf-8') as f:
    migration = json.load(f)

with open('data/whydonate_batch_create.json', 'r', encoding='utf-8') as f:
    batch = json.load(f)

with open('data/whydonate_all_campaigns.json', 'r', encoding='utf-8') as f:
    existing = json.load(f)

print(f"Loaded {len(migration)} migration pending campaigns")
print(f"Loaded {len(batch)} batch create campaigns")
print(f"Loaded {len(existing)} existing WhyDonate campaigns")

# Merge migration and batch, using bid/id/phone as unique key
campaigns_dict = {}

for campaign in migration + batch:
    # Get unique identifier
    uid = campaign.get('bid') or campaign.get('id') or campaign.get('phone') or campaign.get('chuffed_id')
    if uid:
        uid = str(uid)
        # Keep first occurrence (migration takes priority)
        if uid not in campaigns_dict:
            campaigns_dict[uid] = campaign

print(f"\nMerged to {len(campaigns_dict)} unique campaigns")

# Get existing campaign identifiers
existing_ids = set()
for campaign in existing:
    uid = campaign.get('bid') or campaign.get('id') or campaign.get('phone') or campaign.get('chuffed_id')
    if uid:
        existing_ids.add(str(uid))

print(f"Found {len(existing_ids)} existing campaign IDs")

# Filter out campaigns already on WhyDonate
to_create = {uid: campaign for uid, campaign in campaigns_dict.items() if uid not in existing_ids}

print(f"\nCampaigns to create: {len(to_create)}")

# Save the merged list for campaign creation
to_create_list = list(to_create.values())
with open('data/campaigns_to_create_final.json', 'w', encoding='utf-8') as f:
    json.dump(to_create_list, f, ensure_ascii=False, indent=2)

print(f"Saved {len(to_create_list)} campaigns to data/campaigns_to_create_final.json")

# Group by trustee (phone number)
trustee_campaigns = {}
for campaign in to_create_list:
    phone = campaign.get('phone') or campaign.get('bid')
    if phone:
        phone = str(phone)
        if phone not in trustee_campaigns:
            trustee_campaigns[phone] = []
        trustee_campaigns[phone].append(campaign)

print(f"\nGrouped into {len(trustee_campaigns)} trustees")

# Generate bilingual messages for each trustee
output_dir = Path('data/trustee_messages')
output_dir.mkdir(exist_ok=True)

for phone, campaigns in trustee_campaigns.items():
    # Get trustee name from first campaign
    trustee_name = campaigns[0].get('name', 'Trustee')
    
    # Build bilingual message
    message_en = f"Hello {trustee_name},\n\n"
    message_en += f"We have created {len(campaigns)} campaign(s) for you on WhyDonate:\n\n"
    
    message_ar = f"مرحبا {trustee_name}،\n\n"
    message_ar += f"لقد أنشأنا {len(campaigns)} حملة لك على WhyDonate:\n\n"
    
    for i, campaign in enumerate(campaigns, 1):
        title = campaign.get('title', 'Untitled')
        goal = campaign.get('goal', 0)
        
        message_en += f"{i}. {title}\n"
        message_en += f"   Goal: €{goal:,}\n\n"
        
        message_ar += f"{i}. {title}\n"
        message_ar += f"   الهدف: €{goal:,}\n\n"
    
    # Combine English and Arabic
    combined_message = message_en + "\n" + "="*50 + "\n\n" + message_ar
    
    # Save to file
    filename = output_dir / f"{phone}_message.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(combined_message)
    
    print(f"Generated message for {phone}: {len(campaigns)} campaigns")

print(f"\nAll trustee messages saved to {output_dir}")
print("\nSummary:")
print(f"- Total campaigns to create: {len(to_create_list)}")
print(f"- Total trustees: {len(trustee_campaigns)}")
print(f"- Ready for batch creation!")
