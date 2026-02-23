import json
import os
import re
from sovereign_vault import SovereignVault

DATA_FILE = "data/potential_beneficiaries.json"
SUBMISSIONS_DIR = "data/onboarding_submissions"
PORTAL_URL = "https://dours-d.github.io/local-ai-campaign-assistant/index.html#"
VIRAL_URL = "https://dours-d.github.io/local-ai-campaign-assistant/"
NOOR_PORTAL_URL = "https://dours-d.github.io/local-ai-campaign-assistant/brain.html"
OUTBOX_DIR = "data/onboarding_outbox"

def clean_to_digits(s):
    if not s: return ""
    return re.sub(r'\D', '', str(s))

def get_last_9(s):
    digits = clean_to_digits(s)
    return digits[-9:] if len(digits) >= 9 else digits

def generate_messages():
    # 1. Load Sources of Truth
    REGISTRY_FILE = "data/campaign_registry.json"
    registry = {}
    if os.path.exists(REGISTRY_FILE):
        with open(REGISTRY_FILE, 'r', encoding='utf-8') as f:
            registry = json.load(f).get("mappings", {})

    UNIFIED_DB = "data/campaigns_unified.json"
    existing_addresses_by_name = {}
    if os.path.exists(UNIFIED_DB):
        with open(UNIFIED_DB, 'r', encoding='utf-8') as f:
            db = json.load(f)
            for c in db.get('campaigns', []):
                addr = c.get('usdt_address') or c.get('payout_details', {}).get('address')
                if addr:
                    existing_addresses_by_name[c['privacy']['internal_name']] = addr

    # 2. Extract wallets from ONBOARDING SUBMISSIONS (Highest Priority)
    submission_wallets = {}
    if os.path.exists(SUBMISSIONS_DIR):
        for filename in os.listdir(SUBMISSIONS_DIR):
            if filename.endswith("_submission.json"):
                path = os.path.join(SUBMISSIONS_DIR, filename)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        wallet = data.get("personal_wallet")
                        if wallet and wallet.strip():
                            wallet = wallet.strip()
                            # Basic validation: Must look like a TRON or ETH address
                            if re.match(r'^(T[A-Za-z0-9]{33}|0x[A-Fa-f0-9]{40})$', wallet):
                                # Map by full BID and Last 9
                                bid = data.get("beneficiary_id")
                                if bid:
                                    submission_wallets[clean_to_digits(bid)] = wallet
                                    submission_wallets[get_last_9(bid)] = wallet
                except Exception as e:
                    print(f"Error reading submission {filename}: {e}")

    # 3. Collect all active beneficiaries
    all_beneficiaries = {}
    for bid, data in registry.items():
        all_beneficiaries[bid] = {
            "name": data.get('name', 'Resilient Beneficiary'),
            "whydonate": data.get('whydonate_url'),
            "wallet": data.get('wallet_address'),
            "status": "live" if data.get('whydonate_url') else "onboarding"
        }

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            potential = json.load(f)
            for p in potential:
                name = p['name']
                bid = p.get('bid') or "".join([char for char in name if char.isdigit()])
                if not bid: bid = name
                if bid not in all_beneficiaries:
                    all_beneficiaries[bid] = {
                        "name": name,
                        "whydonate": None,
                        "wallet": None,
                        "status": "potential"
                    }

    vault = SovereignVault()
    # No more disqualification. We want these core campaigns to get the same updated template.
    vault_index_by_9 = {}
    
    for key, data in vault.mapping.items():
        l9 = get_last_9(key)
        if l9 and len(l9) == 9:
            if l9 not in vault_index_by_9 or "submission" in key or "viral" in key:
                vault_index_by_9[l9] = (key, data.get('address'))

    os.makedirs(OUTBOX_DIR, exist_ok=True)
    INDIVIDUAL_DIR = os.path.join(OUTBOX_DIR, "individual_messages")
    os.makedirs(INDIVIDUAL_DIR, exist_ok=True)

    stats = {"copied_submission": 0, "copied_vault": 0, "provisioned": 0}

    for bid, info in all_beneficiaries.items():
        name = info['name']
        display_bid = bid.replace("viral_+", "")
        norm_digits = clean_to_digits(bid)
        l9_bid = get_last_9(bid)
        
        # --- ADDRESS RESOLUTION (PRIORITIZED) ---
        address = None
        
        # 1. PRIORITY 1: Registry / Unified DB (Absolute Source of Truth)
        address = info.get('wallet') or existing_addresses_by_name.get(name)
        if address: stats["copied_vault"] += 1
        
        # 2. PRIORITY 2: Manual Submissions
        if not address:
            address = submission_wallets.get(norm_digits) or submission_wallets.get(l9_bid)
            if address: stats["copied_submission"] += 1
        
        # 3. PRIORITY 3: Vault Matching (BIP44 Deterministic)
        if not address:
            if l9_bid in vault_index_by_9:
                _, match_addr = vault_index_by_9[l9_bid]
                address = match_addr
            if not address:
                address = vault.get_address(norm_digits) or \
                          vault.get_address(bid) or \
                          vault.get_address(bid + "_submission")
            if address: stats["copied_vault"] += 1
            
        # 4. FALLBACK: Provision NEW
        if not address:
            key = norm_digits if norm_digits else name
            address = vault.provision_new_address(key)
            stats["provisioned"] += 1

        # --- LINKS ---
        personal_wd = info['whydonate']
        
        # --- MESSAGE GENERATION ---
        ar_onboarding = f"{display_bid}\n"
        ar_onboarding += f"السلام عليكم ورحمة الله وبركاته.\n\n"
        ar_onboarding += f"نحن هنا لنكون شهوداً (Shahada) على صمودكم، ولتفعيل أمانتكم (Amanah) في أعناقنا.\n\n"
        ar_onboarding += f"الخطوة الأولى هي التوثيق عبر **بوابة التعديل السيادي (Sovereign Portal)**. هذا الرابط يحفظ قصتكم وصوركم بعيداً عن أي حذف أو رقابة:\n"
        ar_onboarding += f"🛠 {PORTAL_URL}/onboard/{bid}\n\n"
        ar_onboarding += f"لقد خصصنا لكم **محفظة رقمية (USDT)** فريدة، لضمان وصول المساعدات إليكم مباشرة وسيادة تامة على أموالكم:\n"
        ar_onboarding += f"💰 {address}\n\n"
        
        if personal_wd:
            ar_onboarding += f"🔗 **رابط حملتكم المباشر**: {personal_wd}\n\n"
        else:
            ar_onboarding += f"🔗 **رابط الصندوق الموحد**: {VIRAL_URL}\n"
            ar_onboarding += f"يمكنكم استخدام هذا الرابط مؤقتاً، وتأكدوا من ذكر الـ ID الخاص بكم: {bid} في رسالة المتبرع.\n\n"
            
        ar_onboarding += f"🌍 **بوابة 'نور' المعرفية (Noor Portal)**: نحن نوثق تاريخكم الحي للأجيال القادمة لضمان بقاء الحقيقة في ذاكرة العالم: {NOOR_PORTAL_URL}\n"
        
        en_onboarding = f"Salam Alaykum.\n\n"
        en_onboarding += f"We are establishing your sacred Trust (Amanah). Step 1 is to bear witness (Shahada) to your resilience by verifying your data and media.\n\n"
        en_onboarding += f"🛠 **Sovereign Portal**:\n"
        en_onboarding += f"{PORTAL_URL}/onboard/{bid}\n\n"
        en_onboarding += f"💰 **Digital Wallet (USDT)**:\n"
        en_onboarding += f"{address}\n\n"
        
        if personal_wd:
            en_onboarding += f"🔗 **Your Direct Campaign Link**:\n{personal_wd}\n\n"
        else:
            en_onboarding += f"🔗 **Global Umbrella Fund Link**:\n{VIRAL_URL}\n"
            en_onboarding += f"Donors can use this collective link; ensure they include your ID: {bid}\n\n"
        
        en_onboarding += f"🌍 **Noor Knowledge Portal**: Your resilience is being preserved in our autonomous memory as a sacred record: {NOOR_PORTAL_URL}\n"

        full_onboarding = ar_onboarding + "\n" + "-"*30 + "\n\n" + en_onboarding
        with open(os.path.join(OUTBOX_DIR, f"{display_bid}_onboarding.txt"), 'w', encoding='utf-8') as f:
            f.write(full_onboarding)

        if personal_wd:
            ar_campaign = f"{display_bid}\n"
            ar_campaign += f"السلام عليكم ورحمة الله وبركاته.\n\n"
            ar_campaign += f"حملتكم الآن أمانة (Amanah) مفعلة وجاهزة للنشر! إليك أدواتكم للتمكين:\n\n"
            ar_campaign += f"1️⃣ **رابط النافذة المباشرة (Direct Window)**:\n"
            ar_campaign += f"{personal_wd}\n"
            ar_campaign += f"استخدموا هذا الرابط لمشاركة قصتكم الشخصية مع العالم وبدء جمع التبرعات مباشرة.\n\n"
            ar_campaign += f"2️⃣ **رابط الدرع الجماعي (Collective Shield)**:\n"
            ar_campaign += f"{VIRAL_URL}\n"
            ar_campaign += f"هذا الصندوق يضمن كفاءة أعلى وصفر رسوم تحويل. اطلبو من المتبرعين كتابة الـ ID الخاص بكم: **{bid}** في الملاحظات.\n\n"
            ar_campaign += f"💰 **محفظتكم السيادية (USDT)**:\n"
            ar_campaign += f"{address}\n\n"
            ar_campaign += f"🌍 **بوابة 'نور' المعرفية**: صمودكم محفوظ الآن في الذاكرة المستقلة للعالم ليكون شهادة للأجيال: {NOOR_PORTAL_URL}\n\n"
            
            en_campaign = f"Salam Alaykum.\n\n"
            en_campaign += f"Your campaign is now a live Amanah! Use these links to build your support:\n\n"
            en_campaign += f"1. **Your Direct Window**:\n{personal_wd}\n\n"
            en_campaign += f"2. **The Collective Shield (Umbrella Fund)**:\n{VIRAL_URL}\n"
            en_campaign += f"Ask donors to include ID: **{bid}** for transparent tracking.\n\n"
            en_campaign += f"💰 **Your Sovereign Wallet**:\n{address}\n\n"
            en_campaign += f"🌍 **Noor Knowledge Portal**: Your story is being safeguarded as a witness for the Ummah: {NOOR_PORTAL_URL}\n"

            full_campaign = ar_campaign + "\n" + "-"*30 + "\n\n" + en_campaign
            with open(os.path.join(OUTBOX_DIR, f"{display_bid}_campaign.txt"), 'w', encoding='utf-8') as f:
                f.write(full_campaign)
            
            clean_filename = re.sub(r'[^\w\s-]', '', name).strip().replace(' ', '_')
            indiv_name = f"{display_bid}_{clean_filename}.txt"
            with open(os.path.join(INDIVIDUAL_DIR, indiv_name), 'w', encoding='utf-8') as f:
                f.write(full_campaign)

    print(f"Sync Complete.")
    print(f"Addresses Copied from Submissions: {stats['copied_submission']}")
    print(f"Addresses Copied from Vault/DB: {stats['copied_vault']}")
    print(f"Addresses Provisioned (New): {stats['provisioned']}")

if __name__ == "__main__":
    generate_messages()
