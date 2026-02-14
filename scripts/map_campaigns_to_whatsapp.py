import json
import sys
import io
from pathlib import Path
from collections import defaultdict

# Configure UTF-8 encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Load campaign coupling (chuffed_id -> whatsapp_id mapping)
with open('data/campaign_coupling.json', 'r', encoding='utf-8') as f:
    coupling = json.load(f)

# Load campaigns to create
with open('data/campaigns_to_create_final.json', 'r', encoding='utf-8') as f:
    campaigns_to_create = json.load(f)

print(f"Loaded {len(coupling)} campaign couplings")
print(f"Loaded {len(campaigns_to_create)} campaigns to create")

# Build chuffed_id -> whatsapp_id mapping
chuffed_to_whatsapp = {}
for c in coupling:
    chuffed_id = c.get('chuffed_id')
    whatsapp_id = c.get('whatsapp_id')
    if chuffed_id and whatsapp_id:
        chuffed_to_whatsapp[chuffed_id] = whatsapp_id

print(f"Found {len(chuffed_to_whatsapp)} campaigns with WhatsApp numbers")

# Map campaigns to WhatsApp numbers
campaigns_with_whatsapp = []
campaigns_without_whatsapp = []

for campaign in campaigns_to_create:
    chuffed_id = campaign.get('chuffed_id') or campaign.get('id')
    whatsapp_id = chuffed_to_whatsapp.get(chuffed_id)
    
    if whatsapp_id:
        campaign['whatsapp_id'] = whatsapp_id
        campaigns_with_whatsapp.append(campaign)
    else:
        campaigns_without_whatsapp.append(campaign)

print(f"\nCampaigns with WhatsApp: {len(campaigns_with_whatsapp)}")
print(f"Campaigns without WhatsApp: {len(campaigns_without_whatsapp)}")

if campaigns_without_whatsapp:
    print("\nWARNING: Some campaigns don't have WhatsApp numbers!")
    print("Saving them to data/campaigns_missing_whatsapp.json")
    with open('data/campaigns_missing_whatsapp.json', 'w', encoding='utf-8') as f:
        json.dump(campaigns_without_whatsapp, f, ensure_ascii=False, indent=2)

# Group campaigns by WhatsApp number (trustee)
trustee_campaigns = defaultdict(list)
for campaign in campaigns_with_whatsapp:
    whatsapp_id = campaign['whatsapp_id']
    trustee_campaigns[whatsapp_id].append(campaign)

print(f"\nGrouped into {len(trustee_campaigns)} trustees")

# Generate bilingual messages for each trustee
output_dir = Path('data/trustee_messages')
output_dir.mkdir(exist_ok=True)

for whatsapp_id, campaigns in trustee_campaigns.items():
    # Get trustee name from first campaign
    trustee_name = campaigns[0].get('internal_name') or campaigns[0].get('name') or 'Trustee'
    
    # Build bilingual message
    message_en = f"Hello {trustee_name},\n\n"
    message_en += f"We are creating {len(campaigns)} campaign(s) for you on WhyDonate:\n\n"
    
    message_ar = f"مرحبا {trustee_name}،\n\n"
    message_ar += f"نحن ننشئ {len(campaigns)} حملة لك على WhyDonate:\n\n"
    
    for i, campaign in enumerate(campaigns, 1):
        title = campaign.get('title', 'Untitled')
        goal = campaign.get('goal') or campaign.get('raised', 0)
        
        message_en += f"{i}. {title}\n"
        if goal:
            message_en += f"   Goal: €{goal:,}\n"
        message_en += "\n"
        
        message_ar += f"{i}. {title}\n"
        if goal:
            message_ar += f"   الهدف: €{goal:,}\n"
        message_ar += "\n"
    
    # Combine English and Arabic
    combined_message = message_en + "\n" + "="*60 + "\n\n" + message_ar
    
    # Save to file
    filename = output_dir / f"{whatsapp_id}_message.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(combined_message)
    
    print(f"Generated message for {whatsapp_id}: {len(campaigns)} campaigns")

# Save campaigns with WhatsApp for batch creation
with open('data/campaigns_ready_for_creation.json', 'w', encoding='utf-8') as f:
    json.dump(campaigns_with_whatsapp, f, ensure_ascii=False, indent=2)

print(f"\n✅ All trustee messages saved to {output_dir}")
print(f"✅ Campaigns ready for creation saved to data/campaigns_ready_for_creation.json")
print("\nSummary:")
print(f"- Campaigns ready to create: {len(campaigns_with_whatsapp)}")
print(f"- Campaigns missing WhatsApp: {len(campaigns_without_whatsapp)}")
print(f"- Total trustees: {len(trustee_campaigns)}")
print(f"\nReady for batch creation!")
