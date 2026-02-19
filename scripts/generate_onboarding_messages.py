import json
import os
from sovereign_vault import SovereignVault

DATA_FILE = "data/potential_beneficiaries.json"
PORTAL_URL = "https://dours-d.github.io/local-ai-campaign-assistant/index.html#"
VIRAL_URL = "https://bit.ly/g-gz-resi-fund"
OUTBOX_DIR = "data/onboarding_outbox"

def generate_messages():
    if not os.path.exists(DATA_FILE):
        print("Error: potential_beneficiaries.json not found.")
        return

    # Load registry for Existing Links
    REGISTRY_FILE = "data/campaign_registry.json"
    registry = {}
    if os.path.exists(REGISTRY_FILE):
        with open(REGISTRY_FILE, 'r', encoding='utf-8') as f:
            registry = json.load(f).get("mappings", {})

    # Load Source of Truth for existing addresses
    existing_addresses = {}
    UNIFIED_DB = "data/campaigns_unified.json"
    if os.path.exists(UNIFIED_DB):
        with open(UNIFIED_DB, 'r', encoding='utf-8') as f:
            db = json.load(f)
            for c in db['campaigns']:
                addr = c.get('usdt_address') or c.get('payout_details', {}).get('address')
                if addr:
                    existing_addresses[c['privacy']['internal_name']] = addr

    # Deduplicate and merge contacts
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        contacts_list = json.load(f)
    
    # Map by BID
    all_beneficiaries = {}
    
    # 1. Process Potential Beneficiaries
    for c in contacts_list:
        name = c['name']
        bid = c.get('bid') or "".join([char for char in name if char.isdigit()])
        if not bid: bid = name
        all_beneficiaries[bid] = {"name": name, "source": "potential"}

    # 2. Add Registry Beneficiaries (The "Returned" ones)
    for bid, data in registry.items():
        if bid not in all_beneficiaries:
            all_beneficiaries[bid] = {"name": data.get('name', bid), "source": "registry"}
        # Ensure we favor registry data for names if available
        if data.get('name'):
            all_beneficiaries[bid]['name'] = data['name']

    vault = SovereignVault()
    os.makedirs(OUTBOX_DIR, exist_ok=True)
    
    # Also create individual_messages subfolder
    INDIVIDUAL_DIR = os.path.join(OUTBOX_DIR, "individual_messages")
    os.makedirs(INDIVIDUAL_DIR, exist_ok=True)

    for bid, info in all_beneficiaries.items():
        name = info['name']
        clean_bid = bid.replace("viral_+", "")
        
        # Links
        personal_wd = registry.get(bid, {}).get('whydonate_url')
        
        # Wallet
        address = existing_addresses.get(name) or registry.get(bid, {}).get('wallet_address')
        if not address:
            address = vault.provision_new_address(name)

        # --- PHASE 1: ONBOARDING (Data Collection) ---
        onboarding_msg = f"{clean_bid}\n"
        onboarding_msg += f"السلام عليكم ورحمة الله وبركاته.\n\n"
        onboarding_msg += f"نحن بصدد تفعيل أمانتكم (Amanah) لجمع التبرعات. الخطوة الأولى هي الشهادة (Shahada) على صمودكم من خلال توثيق بياناتكم وصوركم.\n\n"
        onboarding_msg += f"🛠 **بوابة التعديل السيادي (Sovereign Portal)**:\n"
        onboarding_msg += f"{PORTAL_URL}/onboard/{bid}\n"
        onboarding_msg += f"يرجى استخدام هذا الرابط لتحديث قصتكم ورفع صوركم. المعرف الخاص بك (ID) هو: {bid}\n\n"
        onboarding_msg += f"💰 **محفظتكم الرقمية (USDT)**:\n"
        onboarding_msg += f"{address}\n"
        onboarding_msg += f"جميع التبرعات ستصل لهذه المحفظة مباشرة لضمان السيادة المالية والشفافية التامة.\n\n"
        
        if personal_wd:
            onboarding_msg += f"🔗 **رابط حملتكم المباشر**:\n{personal_wd}\n\n"
        else:
            onboarding_msg += f"🔗 **رابط الصندوق الموحد (العام)**:\n"
            onboarding_msg += f"{VIRAL_URL}\n"
            onboarding_msg += f"يمكن للمتبرعين دعمكم عبر هذا الرابط مؤقتاً؛ تأكدوا من ذكر الـ ID الخاص بكم: {bid}\n\n"

        onboarding_msg += f"🌍 **مستودع المعرفة (نور/Dunya)**:\n"
        onboarding_msg += f"نحن نوثق صمودكم للأجيال القادمة عبر ذكاء 'نور' الاصطناعي.\n\n"
        onboarding_msg += "-" * 30 + "\n\n"
        
        # ENGLISH ONBOARDING
        onboarding_msg += f"Salam Alaykum.\n\n"
        onboarding_msg += f"We are establishing your sacred Trust (Amanah). Step 1 is to bear witness (Shahada) to your resilience by verifying your data and media.\n\n"
        onboarding_msg += f"🛠 **Sovereign Portal**:\n"
        onboarding_msg += f"{PORTAL_URL}/onboard/{bid}\n"
        onboarding_msg += f"Use this link to update your story and upload your photos. Your ID: {bid}\n\n"
        onboarding_msg += f"💰 **Digital Wallet (USDT)**:\n"
        onboarding_msg += f"{address}\n\n"
        
        if personal_wd:
            onboarding_msg += f"🔗 **Your Direct Campaign Link**:\n{personal_wd}\n\n"
        else:
            onboarding_msg += f"🔗 **Global Umbrella Fund Link**:\n"
            onboarding_msg += f"{VIRAL_URL}\n"
            onboarding_msg += f"Donors can use this collective link to support you; ensure they include your ID: {bid}\n\n"

        onboarding_msg += f"🌍 **Noor AI (Knowledge Base/Dunya)**:\n"
        onboarding_msg += f"Your resilience is being preserved in our autonomous memory: https://dours-d.github.io/local-ai-campaign-assistant/brain.html\n"

        with open(os.path.join(OUTBOX_DIR, f"{clean_bid}_onboarding.txt"), 'w', encoding='utf-8') as f:
            f.write(onboarding_msg)

        # --- PHASE 2: CAMPAIGN (Links) ---
        if personal_wd:
            campaign_msg = f"{clean_bid}\n"
            campaign_msg += f"السلام عليكم ورحمة الله وبركاته.\n\n"
            campaign_msg += f"حملتكم الآن جاهزة ومفعلة كأمانة (Amanah) مقدسة! إليك الروابط الخاصة بكم:\n\n"
            campaign_msg += f"1️⃣ **رابط حملتكم المباشر (Direct Window)**:\n"
            campaign_msg += f"{personal_wd}\n"
            campaign_msg += f"2️⃣ **صندوق المظلة المشترك (Collective Shield)**:\n"
            campaign_msg += f"{VIRAL_URL}\n"
            campaign_msg += f"💡 **تنبيه**: عند التبرع عبر الصندوق المشترك، يرجى كتابة الـ ID الخاص بك: **{bid}** لضمان الشفافية.\n\n"
            campaign_msg += f"📊 **توضيح الفروقات**:\n"
            campaign_msg += f"🔸 **الرابط الشخصي**: لسرد القصص المباشر وبناء الهوية.\n"
            campaign_msg += f"🔸 **صندوق المظلة**: للكفاءة الجماعية وصفر عمولات تحويل.\n\n"
            campaign_msg += f"🌍 **مستودع المعرفة (نور/Dunya)**:\n"
            campaign_msg += f"قصتكم خالدة الآن في ذكاء 'نور': https://dours-d.github.io/local-ai-campaign-assistant/brain.html\n\n"
            campaign_msg += "-" * 30 + "\n\n"
            
            # ENGLISH CAMPAIGN
            campaign_msg += f"Salam Alaykum.\n\n"
            campaign_msg += f"Your campaign is now live as a sacred Amanah! Here are your links:\n\n"
            campaign_msg += f"1. **Your Direct Campaign Link (Direct Window)**:\n"
            campaign_msg += f"{personal_wd}\n"
            campaign_msg += f"2. **The Umbrella Fund (Collective Shield)**:\n"
            campaign_msg += f"{VIRAL_URL}\n"
            campaign_msg += f"💡 **Important**: Tell donors to include your ID: **{bid}** in the comments for direct tracking.\n\n"
            campaign_msg += f"📊 **Comparison**:\n"
            campaign_msg += f"🔸 **Personal Campaign**: Best for social media sharing and personal storytelling.\n"
            campaign_msg += f"🔸 **Umbrella Fund**: Best for zero-waste collective aid and institutional support.\n\n"
            campaign_msg += f"🌍 **Noor AI (Knowledge Base/Dunya)**:\n"
            campaign_msg += f"Your resilience is immortalized in our knowledge repository.\n"
            
            # Write to both outbox and individual_messages for tracking
            with open(os.path.join(OUTBOX_DIR, f"{clean_bid}_campaign.txt"), 'w', encoding='utf-8') as f:
                f.write(campaign_msg)
            
            indiv_name = f"{clean_bid}_{name.replace(' ', '_')}.txt"
            with open(os.path.join(INDIVIDUAL_DIR, indiv_name), 'w', encoding='utf-8') as f:
                f.write(campaign_msg)
        else:
            with open(os.path.join(OUTBOX_DIR, f"{clean_bid}_campaign_PENDING.txt"), 'w', encoding='utf-8') as f:
                f.write(f"Campaign Link for BID {bid} is being generated...")

    print(f"Generated split messages in {OUTBOX_DIR}")

if __name__ == "__main__":
    generate_messages()
