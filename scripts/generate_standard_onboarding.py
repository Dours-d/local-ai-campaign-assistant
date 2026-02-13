import sys
import os

def generate_standard_message(name_or_id):
    # Base URL for the portal
    PORTAL_URL = "https://dours-d.github.io/local-ai-campaign-assistant/onboard.html"
    
    msg = f"السلام عليكم ورحمة الله وبركاته.\n\n"
    msg += f"يسعدنا مساعدتكم في إطلاق حملتكم لجمع التبرعات عبر منصتنا. نحن بصدد إعداد بياناتكم الأولية.\n\n"
    msg += f"🛠 **بوابة التعديل السيادي (Sovereign Portal)**:\n"
    msg += f"{PORTAL_URL}#{name_or_id}\n\n"
    msg += f"يرجى استخدام هذا الرابط لمراجعة بياناتكم الأولية ورفع الصور والقصة الخاصة بكم.\n"
    msg += f"إذا لم يعمل الرابط المباشر، يمكنك الدخول إلى {PORTAL_URL} وإدخال رقم الواتساب الخاص بك المكون من رمز الدولة ثم الرقم (بدون + أو مسافات).\n\n"
    msg += f"الـ ID الخاص بكم هو: {name_or_id}\n\n"
    msg += f"🌍 **رابط دنيا (الشفافية والذكاء الاصطناعي/Noor)**:\n"
    msg += f"https://dours-d.github.io/local-ai-campaign-assistant/brain.html\n\n"
    msg += f"سيتم ربط حملتكم بمحفظة رقمية لضمان وصول المساعدة كاملة وبأمان.\n\n"
    msg += "-" * 30 + "\n\n"
    msg += f"Salam Alaykum.\n\n"
    msg += f"We are honored to help you launch your fundraising campaign. We are setting up your initial profile.\n\n"
    msg += f"🛠 **Sovereign Portal**:\n"
    msg += f"{PORTAL_URL}#{name_or_id}\n\n"
    msg += f"Use this link to verify your details and upload your photos and story.\n"
    msg += f"If the direct link doesn't work, you can go to {PORTAL_URL} and enter your WhatsApp number (Country code + number, no + or spaces).\n\n"
    msg += f"Your ID is: {name_or_id}\n\n"
    msg += f"🌍 **DUNYA: Digital Intelligence (Noor AI)**:\n"
    msg += f"https://dours-d.github.io/local-ai-campaign-assistant/brain.html\n\n"
    msg += f"Your campaign will be linked to a digital wallet to ensure aid reaches you fully and securely.\n"
    
    return msg

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_standard_onboarding.py <NAME_OR_ID>")
        sys.exit(1)
        
    target = sys.argv[1]
    message = generate_standard_message(target)
    
    # Save to a temporary file for easy copy-pasting
    os.makedirs("data/onboarding_outbox", exist_ok=True)
    out_path = f"data/onboarding_outbox/standard_{target}.txt"
    
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(message)
        
    print(f"\nStandard onboarding message generated for: {target}")
    print(f"File saved to: {out_path}")
    print("\n" + "="*40 + "\n")
    print(message)
    print("\n" + "="*40 + "\n")
