import datetime

def generate_trustee_card(name: str, beneficiary_id: str, whydonate_url: str = None, wallet_address: str = None, private_key: str = None) -> str:
    """
    Generates the unified bilingual Trustee Card block to be appended to all outgoing communications.
    """
    # 1. Defaults & Cleaning
    name = (name or "Unknown").strip()
    bid = str(beneficiary_id or "").strip()
    
    # Clean the whydonate URL to ensure it's not simply an empty string. We do NOT overwrite valid string URLs.
    if whydonate_url and isinstance(whydonate_url, str):
        wd_url = whydonate_url.strip()
    else:
        wd_url = ""
        
    wd_display = wd_url if wd_url else "[PENDING]"
    
    wallet_display = wallet_address.strip() if wallet_address and str(wallet_address).strip() != "" else None
    
    # 2. Timestamp Generation (UTC)
    parsed_date = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    # 3. Wallet Logic
    if wallet_display and wallet_display.lower() != "[wallet_pending]":
        wallet_text = wallet_display
        if private_key:
            pk_text = f"🔑 Private Key / المفتاح الخاص:\n{private_key}\n*(Keep this secret. Whoever holds this key controls this wallet / احتفظوا بهذا المفتاح سراً. من يملكه يملك المحفظة)*"
        else:
            pk_text = ""
    else:
        wallet_text = "[PENDING PROVISIONING]"
        pk_text = ""

    # 4. Standard Links
    collective_shield = "https://dours-d.github.io/local-ai-campaign-assistant/"
    sovereign_portal = "https://dours-d.github.io/local-ai-campaign-assistant/onboard.html"
    noor_portal = "https://dours-d.github.io/local-ai-campaign-assistant/brain.html"

    # 5. Build Block
    card = []
    card.append("=========================================")
    card.append("TRUSTEE CARD / بطاقة الأمين")
    card.append("=========================================")
    card.append(f"Name / الإسم: {name}")
    card.append(f"ID / المعرف: {bid}")
    card.append(f"Generated / تاريخ الإصدار: {parsed_date}")
    card.append("")
    card.append("🔗 Direct Window / النافذة المباشرة:")
    card.append(f"{wd_display}")
    card.append("")
    card.append("🛡️ Collective Shield / الدرع الجماعي:")
    card.append(f"{collective_shield}")
    card.append(f"(Donors must include ID: {bid} / يجب ذكر المعرف: {bid})")
    card.append("")
    card.append("💰 Sovereign Wallet / المحفظة السيادية (USDT-TRC20):")
    card.append(f"{wallet_text}")
    if pk_text:
        card.append(f"{pk_text}")
    card.append("")
    card.append("🛠 Sovereign Portal / بوابة التعديل السيادي:")
    card.append(f"{sovereign_portal}")
    card.append("(Link establishes your relationship via ID or Phone number / لتأكيد بياناتكم عبر المعرف أو رقم الهاتف)")
    card.append("")
    card.append("🌍 Noor Knowledge Portal / بوابة نور المعرفية:")
    card.append(f"{noor_portal}")
    card.append("=========================================")
    
    return "\n".join(card)
