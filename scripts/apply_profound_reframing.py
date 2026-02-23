import os
import re

directory = r"c:\Users\gaelf\Documents\GitHub\local_ai_campaign_assistant\data\onboarding_outbox\individual_messages"

for filename in os.listdir(directory):
    if filename.endswith(".txt"):
        filepath = os.path.join(directory, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.splitlines()
        
        if not lines: continue
        
        bid = lines[0].strip()
        salutation = lines[1].strip() if len(lines) > 1 else "Assalam Alaykum,"
        
        # Try to find the link
        link = ""
        for line in reversed(lines):
            if "whydonate.com" in line:
                link = line.strip().replace("Link: ", "")
                break
        
        # Try to find the vision phrase
        # "1. Your Campaign: This link is your direct tool to receive support. [VISION]"
        # OR "1. Your Sovereign Portal: ..." (if already run)
        vision_match = re.search(r"1\..*?(?:receive support\.|directly\.)\s*(.*)", content)
        vision_phrase = vision_match.group(1).strip() if vision_match else ""
        # If it contains "2. Sharing", cut it off
        if "2. Sharing" in vision_phrase:
            vision_phrase = vision_phrase.split("2. Sharing")[0].strip()

        # Try to find the personalized blessing
        # It's usually the block after the "How this works" list and before "Link:"
        blessing = ""
        try:
            # Find the line starting with "Our relationship"
            for i, line in enumerate(lines):
                if "Our relationship" in line:
                    blessing = line
                    # Take the next line too if it's there and not the link
                    if i + 1 < len(lines) and "Link:" not in lines[i+1] and lines[i+1].strip():
                        blessing += " " + lines[i+1].strip()
                    break
        except:
            pass
            
        # Refine blessing: remove "Our relationship is built on this mutual Trust/Amanah." if it's there
        # we will add it back in the template
        blessing = blessing.replace("Our relationship is built on this mutual Trust.", "").replace("Our relationship is built on this mutual Amanah.", "").strip()

        # BILINGUAL TEMPLATE
        # ------------------
        
        # ARABIC
        ar_msg = f"السلام عليكم ورحمة الله وبركاته.\n\n"
        ar_msg += f"حملتكم على WhyDonate أصبحت مباشرة الآن. لقد أنشأنا هذا المكان كأمانة مقدسة (Amanah). هذا ليس مجرد رابط، بل هو عهد من التضامن والإيمان بيننا وبين المجتمع العالمي الذي يقف معكم.\n\n"
        ar_msg += f"كيف يعمل هذا:\n"
        ar_msg += f"1. بوابة التعديل السيادي (Sovereign Portal): هذا الرابط هو أداتكم للشهادة (Shahada) على صمودكم وتلقي الدعم المباشر. {vision_phrase if vision_phrase else 'يشارك قصتكم ورؤيتكم مع العالم.'}\n"
        ar_msg += f"2. النشر من أجل الأثر: شاركوا هذا الرابط على نطاق واسع. كل مشاركة هي خطوة نحو تحقيق آمالكم.\n"
        ar_msg += f"3. صندوق المظلة الجماعي (Umbrella Fund): حملتكم محمية بدرعنا الجماعي. هذا الصندوق يضمن وصول المساعدات بالكامل: https://dours-d.github.io/local-ai-campaign-assistant/ \n"
        ar_msg += f"4. ذكاء 'نور' (Noor AI): نحن نحفظ إرثكم. يتم تخليد قصتكم في مستودع المعرفة (دنيا)، لضمان عدم نسيان صمودكم أبداً: https://bit.ly/NoorAiPortal\n"
        ar_msg += f"5. الشهادة (Shahada): نحن ندير هذه الأمانة بصدق تام أمام الله وأمامكم. نشهد على صمودكم ونلتزم بضمان وصول كل قيمة مجمعة إليكم كواجب مقدس.\n\n"
        ar_msg += f"علاقتنا مبنية على هذه الأمانة المتبادلة. {blessing if blessing else ''}\n\n"
        ar_msg += f"الرابط: {link}\n"
        
        ar_msg += "\n" + "="*30 + "\n\n"

        # ENGLISH
        en_msg = f"{salutation}\n\n"
        en_msg += f"Your WhyDonate campaign is now live. We have established this space for you as a sacred Trust (Amanah). This is not just a link; it is a bond of solidarity and faith between us and the global community.\n\n"
        en_msg += f"How this works:\n"
        en_msg += f"1. Your Sovereign Portal: This link is your tool to bear witness (Shahada) to your resilience and receive support directly. {vision_phrase if vision_phrase else 'It shares your story and vision with the world.'}\n"
        en_msg += f"2. Sharing for Impact: Share this link widely. Each share is a step toward making your hope a reality.\n"
        en_msg += f"3. The Collective Umbrella Fund: Your campaign is protected by our collective Shield: https://dours-d.github.io/local-ai-campaign-assistant/ \n"
        en_msg += f"4. Noor AI (Repository of Knowledge): We are preserving your legacy. Your story is being immortalized in the Noor AI Knowledge Base (Dunya): https://bit.ly/NoorAiPortal\n"
        en_msg += f"5. Bearing Witness (Shahada): We handle the administration of this Amanah with total honesty before Allah and you. We bear witness to your resilience and are committed to ensuring that every bit of value raised reaches you as a sacred duty.\n\n"
        en_msg += f"Our relationship is built on this mutual Amanah. {blessing if blessing else ''}\n\n"
        en_msg += f"Link: {link}\n"

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(bid + "\n" + ar_msg + en_msg)

print("Applied profound, bilingual modifications with Umbrella Fund and Noor AI to all messages.")
