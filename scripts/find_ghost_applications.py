import json
import os
import re

def normalize(phone):
    if not phone: return ""
    return re.sub(r'\D', '', str(phone))

def normalize_phone(phone):
    if not phone: return ""
    # Only normalize if it looks like a phone number (mostly digits)
    digits = re.sub(r'\D', '', str(phone))
    if len(digits) >= 7:
        return digits
    return str(phone).strip()

def find_ghosts():
    # Load Registry (Source of Truth for LIVE)
    registry_path = 'campaign_index_full.json'
    if not os.path.exists(registry_path):
        print(f"Error: {registry_path} not found.")
        return

    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = json.load(f)

    # Build a set of IDs/Phones that ARE LIVE
    live_identities = set()
    for key, entry in registry.items():
        live_identities.add(normalize_phone(key))
        if 'beneficiary_id' in entry:
            live_identities.add(normalize_phone(entry['beneficiary_id']))
        # Also check chuffed ID and slug
        if 'chuffed' in entry:
            live_identities.add(str(entry['chuffed'].get('id', '')))
            live_identities.add(str(entry['chuffed'].get('slug', '')))

    # Load Submissions Pool
    submissions_path = 'data/extracted_real_submissions.json'
    submissions = []
    if os.path.exists(submissions_path):
        with open(submissions_path, 'r', encoding='utf-8') as f:
            submissions = json.load(f)

    # Load Missing Migration Queue
    missing_path = 'data/whydonate_missing.json'
    missing_migrations = []
    if os.path.exists(missing_path):
        with open(missing_path, 'r', encoding='utf-8') as f:
            missing_migrations = json.load(f)

    potential_campaigns = []

    # Check Submissions
    for sub in submissions:
        bid = sub.get('bid', '')
        phone = sub.get('whatsapp', '')
        
        if normalize_phone(bid) not in live_identities and normalize_phone(phone) not in live_identities:
            # This is a GHOST from the onboarding form
            title = sub.get('title', '').strip()
            story = sub.get('story', '').strip()
            image = sub.get('image')
            
            tier = "Needs Details"
            if title and story and image:
                tier = "Ready for Manual Creation"
            elif title or story or image:
                tier = "Partial Data"

            potential_campaigns.append({
                "id": bid,
                "name": phone,
                "title": title,
                "tier": tier,
                "source": "onboarding_submission",
                "has_image": bool(image)
            })

    # Check Migrations
    for mig in missing_migrations:
        slug = mig.get('slug', '')
        mid = str(mig.get('id', ''))
        
        if mid not in live_identities and slug not in live_identities:
            potential_campaigns.append({
                "id": mid,
                "name": slug,
                "title": mig.get('title', ''),
                "tier": "Migration (Ready if image exists)",
                "source": "chuffed_migration",
                "has_image": bool(mig.get('image'))
            })


    # Generate Report
    report_path = 'data/potential_campaigns_report.md'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# 👻 Ghost Recovery: Potential Manual Campaign Creations\n\n")
        f.write(f"Total potential candidates found: **{len(potential_campaigns)}**\n\n")
        
        tiers = ["Ready for Manual Creation", "Migration (Ready if image exists)", "Partial Data", "Needs Details"]
        
        for tier in tiers:
            f.write(f"## 🛠️ Tier: {tier}\n")
            tier_items = [p for p in potential_campaigns if p['tier'] == tier]
            if not tier_items:
                f.write("No candidates in this tier.\n\n")
                continue
            
            f.write("| ID | Name/Slug | Title | Has Image | Source |\n")
            f.write("|---|---|---|---|---|\n")
            for item in tier_items:
                title_short = (item['title'][:50] + '...') if len(item['title']) > 50 else item['title']
                f.write(f"| {item['id']} | {item['name']} | {title_short} | {'✅' if item['has_image'] else '❌'} | {item['source']} |\n")
            f.write("\n")

    print(f"Report generated: {report_path}")
    print(f"Found {len(potential_campaigns)} ghosted applications.")

if __name__ == "__main__":
    find_ghosts()
