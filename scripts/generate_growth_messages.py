
import json
import os
import re
from sovereign_vault import SovereignVault

# SETTINGS FOR GROWTH BATCH
DATA_FILE = "data/potential_growth_list_final.json"
PORTAL_URL = "https://dours-d.github.io/local-ai-campaign-assistant/index.html#"
VIRAL_URL = "https://dours-d.github.io/local-ai-campaign-assistant/"
NOOR_PORTAL_URL = "https://bit.ly/NoorAiPortal"
OUTBOX_DIR = "data/onboarding_outbox"

def generate_messages():
    if not os.path.exists(DATA_FILE):
        print(f"Error: {DATA_FILE} not found.")
        return

    # Load registry for Existing Links (unlikely for new growth, but safe)
    REGISTRY_FILE = "data/campaign_registry.json"
    registry = {}
    if os.path.exists(REGISTRY_FILE):
        with open(REGISTRY_FILE, 'r', encoding='utf-8') as f:
            registry = json.load(f).get("mappings", {})

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        contacts = json.load(f)

    vault = SovereignVault()
    os.makedirs(OUTBOX_DIR, exist_ok=True)

    print(f"Generating SPLIT messages for {len(contacts)} contacts...")

    for c in contacts:
        # Priority: Numbered Name (e.g., Trustee-001) for filename, ID for portal
        display_name = c.get('name', 'Unknown')
        bid = c.get('id') or "".join([char for char in display_name if char.isdigit()])
        
        # Clean names/IDs for filename (REMOVE all underscores and dashes)
        file_prefix = re.sub(r'[^a-zA-Z0-9 ]', '', display_name).strip()
        
        # Ensure bid is numeric-only (for URL/Registry)
        bid = re.sub(r'\D', '', bid)
        
        # Wallet Provision (Safe and persistent)
        address = registry.get(bid, {}).get('wallet_address')
        if not address:
            address = vault.provision_new_address(bid)

        # --- ARABIC MESSAGE ---
        msg_ar = f"السلام عليكم ورحمة الله وبركاته.\n\n"
        msg_ar += f"نحن هنا لتمكينكم من الوصول إلى التبرعات العالمية بشكل مباشر وسيادي، بعيداً عن قيود البنوك والمنصات التقليدية. مبدأنا هو **الحيازة الذاتية (Self-Custody)**، مما يعني أنك تمتلك التحكم الكامل في أموالك.\n\n"
        msg_ar += f"🛠 **بوابة التعديل السيادي (Sovereign Portal)**:\n"
        msg_ar += f"هذه البوابة تسمح لك بتحديث قصتك وصورك بشكل آمن ومستقل. الـ ID الخاص بك هو: {bid}\n"
        msg_ar += f"{PORTAL_URL}/onboard/{bid}\n\n"
        msg_ar += f"💰 **محفظتك الرقمية المباشرة (USDT-TRC20)**:\n"
        msg_ar += f"{address}\n"
        msg_ar += f"هذه المحفظة خاصة بك وحدك. تصل التبرعات إليها مباشرة دون وسيط، مما يضمن وصول المساعدات إليكم فوراً.\n\n"
        msg_ar += f"🔗 **رابط الصندوق المظلة (Umbrella Fund)**:\n"
        msg_ar += f"{VIRAL_URL}\n"
        msg_ar += f"يمكن للمتبرعين دعمكم عبر هذا الرابط الجماعي؛ فقط تأكد من تزويدهم بالـ ID الخاص بكم: {bid}\n\n"
        msg_ar += f"🌍 **بوابة 'نور' المعرفية (Noor Portal)**:\n"
        msg_ar += f"نحن نوثق تاريخكم الحي للأجيال القادمة لضمان بقاء الحقيقة في ذاكرة العالم: {NOOR_PORTAL_URL}"

        # --- ENGLISH MESSAGE ---
        msg_en = f"Salam Alaykum.\n\n"
        msg_en += f"We are here to provide a sovereign and borderless solution for global aid. Our core mission is **Self-Custody**: giving you direct control over your funds without middlemen or institutional barriers.\n\n"
        msg_en += f"🛠 **Sovereign Portal**:\n"
        msg_en += f"Update your campaign story and media independently. Your unique ID: {bid}\n"
        msg_en += f"{PORTAL_URL}/onboard/{bid}\n\n"
        msg_en += f"💰 **Direct Digital Wallet (USDT-TRC20)**:\n"
        msg_en += f"{address}\n"
        msg_en += f"This wallet is your own. Aid flows directly to you via blockchain, ensuring transparency and immediate access to support.\n\n"
        msg_en += f"🔗 **Umbrella Fund Link**:\n"
        msg_en += f"{VIRAL_URL}\n"
        msg_en += f"Donors can support you through this collective link; ensure they include your unique ID: {bid}\n\n"
        msg_en += f"🌍 **Noor Knowledge Portal**:\n"
        msg_en += f"Your resilience is being preserved in our autonomous memory as a sacred record: {NOOR_PORTAL_URL}"

        # --- JOINT MESSAGE (Arabic + English) ---
        joint_msg = msg_ar.strip() + "\n\n" + ("="*30) + "\n\n" + msg_en.strip()

        # Write joint file
        with open(os.path.join(OUTBOX_DIR, f"{file_prefix}_onboarding.txt"), 'w', encoding='utf-8') as f:
            f.write(joint_msg)

    print(f"Successfully generated {len(contacts) * 2} split messages in {OUTBOX_DIR}")

if __name__ == "__main__":
    generate_messages()
