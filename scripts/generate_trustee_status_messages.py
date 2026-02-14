import json
import os
from pathlib import Path

def generate_trustee_messages():
    with open('data/extracted_real_submissions.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    output_dir = Path('data/trustee_messages')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Translation map for the English message (I am the LLM, I can provide the Arabic)
    msg_template_en = "Hello! We have successfully received your form submission. We are preparing your campaign on WhyDonate. We will send you the link as soon as it is live. Thank you for your patience."
    msg_template_ar = "مرحبا! لقد استلمنا بنجاح طلبك. نحن نقوم بإعداد حملتك على WhyDonate. سنرسل لك الرابط بمجرد نشره. شكراً لك على صبرك."
    
    for item in data:
        bid = item['bid']
        whatsapp = item['whatsapp']
        
        filename = f"{whatsapp}_status_update.txt"
        filepath = output_dir / filename
        
        content = f"{msg_template_ar}\n\n---\n\n{msg_template_en}"
        
        with open(filepath, 'w', encoding='utf-8') as out:
            out.write(content)
            
    print(f"Generated {len(data)} status update messages in {output_dir}")

if __name__ == "__main__":
    generate_trustee_messages()
