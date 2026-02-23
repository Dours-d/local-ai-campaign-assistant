import json
import re
import os

def generate_bilingual_message(chuffed_id, mission_key, title):
    # If we don't have a mission key, fallback to the ID
    identifier = mission_key if mission_key and mission_key != "N/A" else chuffed_id

    ar_msg = f"""--- MESSAGE FOR {identifier} ---
{identifier}
السلام عليكم ورحمة الله وبركاته.

حملتكم الآن أمانة (Amanah) مفعلة وجاهزة للنشر! إليك أدواتكم للتمكين:

1️⃣ **رابط النافذة المباشرة (Direct Window)**:
[INSERT WHYDONATE LINK HERE]
استخدموا هذا الرابط لمشاركة قصتكم الشخصية مع العالم وبدء جمع التبرعات مباشرة.

2️⃣ **رابط الدرع الجماعي (مشروع قيد التطوير - Project Status)**:
https://dours-d.github.io/local-ai-campaign-assistant/
هذا الصندوق يضمن كفاءة أعلى وصفر رسوم تحويل. اطلبو من المتبرعين كتابة الـ ID الخاص بكم: **{identifier}** في الملاحظات.

🌍 **بوابة 'نور' المعرفية**: صمودكم محفوظ الآن في الذاكرة المستقلة للعالم ليكون شهادة للأجيال: https://dours-d.github.io/local-ai-campaign-assistant/brain.html
"""

    en_msg = f"""
------------------------------

Salam Alaykum.

Your campaign is now a live Amanah! Use these links to build your support:

1. **Your Direct Window**:
[INSERT WHYDONATE LINK HERE]

2. **The Collective Shield (Project Status - Not Reconciled)**:
https://dours-d.github.io/local-ai-campaign-assistant/
Ask donors to include ID: **{identifier}** for transparent tracking.

🌍 **Noor Knowledge Portal**: Your story is being safeguarded as a witness for the Ummah: https://dours-d.github.io/local-ai-campaign-assistant/brain.html

------------------------------
"""
    return ar_msg + en_msg

def main():
    print("Reading final real growth list for dropped IDs...")
    with open('data/final_real_growth_list.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    try:
        dropped_section = content.split('## ❌ Dropped (Missing WhatsApp Anchor)')[1]
        raw_ids = re.findall(r'- (.*)', dropped_section)
    except IndexError:
        raw_ids = []
        
    dropped_ids = []
    for rid in raw_ids:
        # User left notes next to IDs in the markdown, so we just take the first word
        rid = rid.strip().split()[0]
        if rid.startswith('viral_'):
            dropped_ids.append(rid)
        else:
            dropped_ids.append(f"chuffed_{rid}")
            
    print(f"Loaded {len(dropped_ids)} dropped IDs")
    
    # Load batch queue (primary source of best title/desc/image)
    try:
        with open('data/batch_queue.json', 'r', encoding='utf-8') as f:
            batch_queue = json.load(f)
            batch_map = {item['bid']: item for item in batch_queue}
    except FileNotFoundError:
        batch_map = {}
        
    out_dir = 'data/dropped_campaigns_ready_for_creation'
    os.makedirs(out_dir, exist_ok=True)
    
    for c_id in dropped_ids:
        title = "N/A"
        story = "N/A"
        image = "N/A"
        mission_key = "N/A"
        
        # We try to get from batch_queue first
        if c_id in batch_map:
            campaign = batch_map[c_id]
            title = campaign.get('title', "N/A")
            story = campaign.get('description', campaign.get('story', "N/A"))
            image = campaign.get('image', "N/A")
            
            # Extract mission key if present in the story
            mission_match = re.search(r'Beneficiary ID:\s*([^\n]+)', story)
            if mission_match:
                mission_key = mission_match.group(1).strip()
        
        # Build the final output text
        card_content = f"# Campaign Data Pack: {c_id}\n\n"
        card_content += f"## 📝 1. Campaign Title:\n{title}\n\n"
        
        story_formatted = story.replace('\n', '\n> ') if story != "N/A" else story
        card_content += f"## 📖 2. Campaign Story:\n> {story_formatted}\n\n"
        
        card_content += f"## 🖼️ 3. Featured Image:\n"
        if image != "N/A" and image:
            card_content += f"**Local File Path:** `{image}`\n"
        else:
            card_content += f"No image available.\n"
            
        card_content += "\n======================================================\n\n"
        card_content += f"## � 4. Bilingual Onboarding Message\n"
        card_content += "*Copy and send this message to the beneficiary (if found) AFTER creating their WhyDonate campaign.*\n\n"
        
        msg = generate_bilingual_message(c_id, mission_key, title)
        card_content += msg
        
        file_path = os.path.join(out_dir, f"{c_id}.txt")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(card_content)
            
    print(f"Successfully assembled {len(dropped_ids)} campaign packs in {out_dir}")

if __name__ == '__main__':
    main()
