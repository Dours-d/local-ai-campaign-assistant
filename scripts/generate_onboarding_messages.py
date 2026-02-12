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

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        contacts = json.load(f)

    vault = SovereignVault()
    os.makedirs(OUTBOX_DIR, exist_ok=True)

    for c in contacts:
        name = c['name']
        
        # Identification
        bid = c.get('bid') or "".join([char for char in name if char.isdigit()])
        if not bid: bid = name
        clean_bid = bid.replace("viral_+", "")
        
        # Links
        personal_wd = registry.get(bid, {}).get('whydonate_url')
        
        # Wallet
        address = existing_addresses.get(name) or registry.get(bid, {}).get('wallet_address')
        if not address:
            address = vault.provision_new_address(name)

        # --- PHASE 1: ONBOARDING (Data Collection) ---
        onboarding_msg = f"السلام عليكم ورحمة الله وبركاته.\n\n"
        onboarding_msg += f"نحن بصدد تفعيل حملتكم لجمع التبرعات. الخطوة الأولى هي التأكد من بياناتكم وصوركم.\n\n"
        onboarding_msg += f"🛠 **بوابة التعديل السيادي (Sovereign Portal)**:\n"
        onboarding_msg += f"{PORTAL_URL}/onboard/{bid}\n"
        onboarding_msg += f"يرجى استخدام هذا الرابط لتحديث قصتك، صورك، وبياناتك. الـ ID الخاص بك هو: {bid}\n\n"
        onboarding_msg += f"💰 **محفظتك الرقمية (USDT-TRC20)**:\n"
        onboarding_msg += f"{address}\n"
        onboarding_msg += f"جميع التبرعات ستصل لهذه المحفظة مباشرة.\n\n"
        onboarding_msg += f"🔗 **رابط الصندوق الموحد (العام)**:\n"
        onboarding_msg += f"{VIRAL_URL}\n"
        onboarding_msg += f"يمكن للمتبرعين دعمكم عبر هذا الرابط مؤقتاً بكتابة الـ ID الخاص بكم: {bid}\n"
        onboarding_msg += f"\n" + "-"*30 + "\n"
        onboarding_msg += f"Salam Alaykum.\n\n"
        onboarding_msg += f"We are setting up your fundraising campaign. Step 1 is verifying your data and media.\n\n"
        onboarding_msg += f"🛠 **Sovereign Portal**:\n"
        onboarding_msg += f"{PORTAL_URL}/onboard/{bid}\n"
        onboarding_msg += f"Use this link to update your story and upload your photos. Your ID: {bid}\n\n"
        onboarding_msg += f"💰 **Digital Wallet (USDT-TRC20)**:\n"
        onboarding_msg += f"{address}\n\n"
        onboarding_msg += f"🔗 **General Umbrella Fund Link**:\n"
        onboarding_msg += f"{VIRAL_URL}\n"
        onboarding_msg += f"Donors can use this collective link to support you; just ensure they include your ID: {bid}\n"

        with open(os.path.join(OUTBOX_DIR, f"{clean_bid}_onboarding.txt"), 'w', encoding='utf-8') as f:
            f.write(onboarding_msg)

        # --- PHASE 2: CAMPAIGN (Links) ---
        if personal_wd:
            campaign_msg = f"السلام عليكم.\n\n"
            campaign_msg += f"حملتكم الآن جاهزة ومفعلة! إليك الروابط الخاصة بكم:\n\n"
            campaign_msg += f"1️⃣ **رابطك الشخصي (Direct Window)**:\n"
            campaign_msg += f"{personal_wd}\n"
            campaign_msg += f"2️⃣ **الصندوق المشترك (Umbrella Fund)**:\n"
            campaign_msg += f"{VIRAL_URL}\n"
            campaign_msg += f"💡 **تنبيه هام**: عند التبرع عبر الصندوق المشترك، يرجى إخبار المتبرعين بكتابة الـ ID الخاص بك: **{bid}** في التعليقات.\n\n"
            campaign_msg += f"📊 **توضيح الفروقات**:\n\n"
            campaign_msg += f"🔸 **الرابط الشخصي (Direct)**:\n"
            campaign_msg += f"• الهدف: سرد القصص المباشر والوصول للجمهور.\n"
            campaign_msg += f"• الفائدة: بناء هوية مستقلة لحملتكم.\n\n"
            campaign_msg += f"🔸 **الصندوق الموحد (Umbrella)**:\n"
            campaign_msg += f"• الهدف: الكفاءة الجماعية وسرعة الدفع.\n"
            campaign_msg += f"• الفائدة: صفر عمولات تحويل (تصلكم المساعدة كاملة).\n\n"
            campaign_msg += f"\n" + "-"*30 + "\n"
            campaign_msg += f"Salam Alaykum.\n\n"
            campaign_msg += f"Your campaign is now live! Here are your links:\n\n"
            campaign_msg += f"1. **Your Personal Campaign (Direct Window)**:\n"
            campaign_msg += f"{personal_wd}\n"
            campaign_msg += f"2. **The Umbrella Fund (Collective Shield)**:\n"
            campaign_msg += f"{VIRAL_URL}\n"
            campaign_msg += f"💡 **Important**: Tell donors using the Umbrella Fund to include your ID: **{bid}** in the comments.\n\n"
            campaign_msg += f"📊 **Comparison**:\n\n"
            campaign_msg += f"🔸 **Personal Campaign (Direct)**:\n"
            campaign_msg += f"• Best For: Social Media Sharing & Direct Outreach.\n"
            campaign_msg += f"• Benefit: Telling your family's personal story.\n\n"
            campaign_msg += f"🔸 **Umbrella Fund (Collective)**:\n"
            campaign_msg += f"• Best For: Large Grants & Institutional Support.\n"
            campaign_msg += f"• Benefit: Zero transfer fees (maximizing aid).\n\n"
            
            with open(os.path.join(OUTBOX_DIR, f"{clean_bid}_campaign.txt"), 'w', encoding='utf-8') as f:
                f.write(campaign_msg)
        else:
            # If no WD link, we only create a placeholder or don't generate the file
            # For now, let's create a placeholder to show it's pending
            with open(os.path.join(OUTBOX_DIR, f"{clean_bid}_campaign_PENDING.txt"), 'w', encoding='utf-8') as f:
                f.write("Campaign Link is being generated...")

    print(f"Generated split messages in {OUTBOX_DIR}")

if __name__ == "__main__":
    generate_messages()
