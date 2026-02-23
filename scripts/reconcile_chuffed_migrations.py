import json
import os
import re
import requests
import datetime
from urllib.parse import urlparse

# --- CONFIGURATION ---
DATA_DIR = "data"
CHUFFED_BATCH_FILE = os.path.join(DATA_DIR, "launchgood_batch_create.json")
QUEUE_FILE = os.path.join(DATA_DIR, "batch_queue.json")
REGISTRY_FILE = os.path.join(DATA_DIR, "campaign_registry.json")
OUTBOX_DIR = os.path.join(DATA_DIR, "onboarding_outbox", "chuffed_migrations")
MEDIA_DIR = os.path.join(DATA_DIR, "chuffed_media")
os.makedirs(OUTBOX_DIR, exist_ok=True)
os.makedirs(MEDIA_DIR, exist_ok=True)

# URL Constants
PORTAL_URL = "https://dours-d.github.io/local-ai-campaign-assistant/index.html#"
VIRAL_URL = "https://dours-d.github.io/local-ai-campaign-assistant/"
NOOR_PORTAL_URL = "https://bit.ly/NoorAiPortal"

def clean_html(raw_html):
    """Remove HTML tags from description."""
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext.strip()

def download_image(url, campaign_id):
    """Download image to local media folder."""
    try:
        if not url: return None
        response = requests.get(url, stream=True, timeout=10)
        if response.status_code == 200:
            parsed = urlparse(url)
            ext = os.path.splitext(parsed.path)[1]
            if not ext: ext = ".jpg"
            filename = f"{campaign_id}{ext}"
            filepath = os.path.join(MEDIA_DIR, filename)
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            return os.path.abspath(filepath)
    except Exception as e:
        print(f"Failed to download image for {campaign_id}: {e}")
    return None

def generate_onboarding_message(campaign, issue_reason):
    """Generate a bilingual onboarding message for failed migrations."""
    bid = campaign.get('id', 'Unknown')
    title = campaign.get('title', 'Unknown Campaign')
    
    # Attempt to extract phone number if present in ID or elsewhere (a guess)
    phone_match = re.search(r'\+?\d{9,15}', bid)
    phone = phone_match.group(0) if phone_match else "UNKNOWN_PHONE"
    
    msg = f"PHONE NUMBER: {phone}\n"
    msg += f"CAMPAIGN ID: {bid}\n"
    msg += f"ISSUE: {issue_reason}\n"
    msg += "="*30 + "\n\n"
    
    # Arabic Section
    msg += "السلام عليكم ورحمة الله وبركاته.\n\n"
    msg += "نحن هنا لدعمكم. لقد حاولنا نقل حملتكم، لكن البيانات الحالية غير مكتملة أو لم تعد متاحة.\n"
    msg += "لا تقلقوا، مكانكم محفوظ معنا. نرجو منكم تحديث بياناتكم عبر الرابط أدناه لنتمكن من إطلاق حملتكم فوراً.\n\n"
    msg += f"🛠 **بوابة التعديل السيادي (Sovereign Portal)**:\n"
    msg += f"{PORTAL_URL}/onboard/{bid}\n\n"
    msg += f"💰 **محفظتك الرقمية (USDT)**:\n"
    msg += f"(سيتم تفعيلها فور التحديث)\n\n"
    msg += f"🌍 **إرثكم في 'نور' (Noor AI)**:\n{NOOR_PORTAL_URL}\n\n"
    
    msg += "="*30 + "\n\n"
    
    # English Section
    msg += "Salam Alaykum.\n\n"
    msg += "We are here to support you. We attempted to migrate your campaign, but the current data is incomplete or no longer available.\n"
    msg += "Do not worry, your place is reserved with us. Please update your details via the link below so we can launch your campaign immediately.\n\n"
    msg += f"🛠 **Sovereign Portal**:\n"
    msg += f"{PORTAL_URL}/onboard/{bid}\n\n"
    msg += f"💰 **Digital Wallet (USDT)**:\n"
    msg += f"(Will be activated upon update)\n\n"
    msg += f"🌍 **Your Legacy in Noor AI**:\n{NOOR_PORTAL_URL}\n"
    
    filename = f"{bid}_welcome.txt"
    with open(os.path.join(OUTBOX_DIR, filename), 'w', encoding='utf-8') as f:
        f.write(msg)
    return filename

def main():
    print("Starting Chuffed Migration & Onboarding Process...")
    
    # 1. Load Data
    if not os.path.exists(CHUFFED_BATCH_FILE):
        print("No Chuffed batch file found.")
        return

    with open(CHUFFED_BATCH_FILE, 'r', encoding='utf-8') as f:
        chuffed_campaigns = json.load(f)
        
    registry = {}
    if os.path.exists(REGISTRY_FILE):
        with open(REGISTRY_FILE, 'r', encoding='utf-8') as f:
            registry = json.load(f).get("mappings", {})

    queue = []
    if os.path.exists(QUEUE_FILE):
        with open(QUEUE_FILE, 'r', encoding='utf-8') as f:
            queue = json.load(f)
    
    existing_bids = set([c['bid'] for c in queue]) | set(registry.keys())
    
    processed_count = 0
    migrated_count = 0
    onboarding_count = 0

    # 2. Process Campaigns
    for camp in chuffed_campaigns:
        cid = camp.get('id')
        
        # SKIP if already in registry or queue
        if cid in existing_bids:
            continue
            
        processed_count += 1
        
        # CHECK DATA QUALITY
        title = camp.get('title')
        story_html = camp.get('story', '')
        image_url = camp.get('image')
        
        # Condition 1: Missing critical data -> Onboarding
        if not title or not story_html or not image_url:
            generate_onboarding_message(camp, "Missing Title/Story/Image")
            onboarding_count += 1
            print(f"[{cid}] -> Onboarding (Missing Data)")
            continue
            
        # Condition 2: Image Download Fail -> Onboarding
        local_image_path = download_image(image_url, cid)
        if not local_image_path:
            generate_onboarding_message(camp, "Image Download Failed (Deleted on Source?)")
            onboarding_count += 1
            print(f"[{cid}] -> Onboarding (Image Fail)")
            continue
            
        # SUCCESS: Add to Batch Queue
        description = clean_html(story_html)
        
        new_entry = {
            "bid": cid,
            "title": title[:100], # Trucate for safety
            "description": description, # Full description
            "goal": camp.get('goal', 5000),
            "image": local_image_path
        }
        
        queue.append(new_entry)
        migrated_count += 1
        print(f"[{cid}] -> Migrated to Queue")

    # 3. Save Updates
    with open(QUEUE_FILE, 'w', encoding='utf-8') as f:
        json.dump(queue, f, indent=2)
        
    print(f"\n--- SUMMARY ---")
    print(f"Processed: {processed_count}")
    print(f"Migrated to WhyDonate Queue: {migrated_count}")
    print(f"Sent to Onboarding (Missing Data): {onboarding_count}")
    print(f"Output Directory: {OUTBOX_DIR}")

if __name__ == "__main__":
    main()
