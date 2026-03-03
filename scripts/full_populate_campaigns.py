import json
import os
import re

# Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY_PATH = os.path.join(BASE_DIR, 'vault', 'UNIFIED_REGISTRY.json')

def slugify(text):
    return re.sub(r'\W+', '_', text.strip()).lower().strip('_')

def get_full_campaign_data():
    
    with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Filter for items with a whydonate_url and identity_name
    campaigns = []
    seen_urls = set()
    
    for entry in data:
        name = entry.get('identity_name', 'Unknown')
        url = entry.get('whydonate_url')
        if not url or url in seen_urls: continue
        seen_urls.add(url)
        
        # Clean up title: Use full English | Arabic format from registry
        raw_title = entry.get('title', name)
        if ' | ' in raw_title:
            en_title, ar_title = raw_title.split(' | ', 1)
        else:
            en_title = raw_title
            ar_title = name # Fallback
            
        # Description: Use full story (English part if bilingual)
        desc = entry.get('description', '')
        if '---' in desc: 
            desc = desc.split('---')[0].strip() # Take EN part
        
        # Image Logic
        img_path = entry.get('image', '')
        has_real_pic = False
        final_img_url = "https://images.unsplash.com/photo-1488521787991-ed7bbaae773c?auto=format&fit=crop&q=80&w=800"
        
        if img_path:
            # Check if it looks like an authentic picture path
            if 'IMG__' in img_path or 'viral_' in img_path or 'scraped_whydonate' in img_path:
                has_real_pic = True
            
            # Split the path and try both 'data' and 'vault'
            rel_path = ""
            if 'local_ai_campaign_assistant' in img_path:
                rel_path = img_path.split('local_ai_campaign_assistant')[-1].replace('\\', '/').lstrip('/')
            elif os.path.isabs(img_path):
                 # Fallback for other absolute paths
                 rel_path = "data/onboarding_submissions/media/" + os.path.basename(img_path)
            
            if rel_path:
                # Check where it actually exists
                abs_data = os.path.join(BASE_DIR, rel_path.replace('vault/', 'data/'))
                abs_vault = os.path.join(BASE_DIR, rel_path.replace('data/', 'vault/'))
                
                if os.path.exists(abs_vault):
                    final_img_url = "../" + rel_path.replace('data/', 'vault/')
                elif os.path.exists(abs_data):
                    final_img_url = "../" + rel_path.replace('vault/', 'data/')
                else:
                    # If not found in either, still try to use the one from registry but point to data as default
                    final_img_url = "../" + rel_path
        
        c_data = {
            "id": slugify(name),
            "name": name,
            "ar": ar_title,
            "en": en_title,
            "description": desc,
            "url": url,
            "image": final_img_url,
            "has_real_pic": has_real_pic,
            "priority": 1 if "abdullah" in name.lower() and "hoping" in name.lower() else 0
        }
        campaigns.append(c_data)
            
    # Sorting Algorithm:
    # 1. Priority (Abdullah)
    # 2. Real Pictures
    # 3. Alphabetical/Other
    
    campaigns.sort(key=lambda x: (-x['priority'], -1 if x['has_real_pic'] else 0, x['en']))
    
    return campaigns

def generate_cards_html(campaigns):
    html = ""
    for i, c in enumerate(campaigns):
        delay = (i % 3) * 100
        html += f'''
                    <!-- {c['name']} -->
                    <div class="card" data-aos="fade-up" data-aos-delay="{delay}">
                        <div class="card-status" data-campaign-id="{c['id']}"><span class="status-dot active"></span> TRUST VERIFIED</div>
                        <img src="{c['image']}" class="card-img" alt="{c['en']}">
                        <h3 class="lang-dual"><span class="ar-main">{c['ar']}</span><span class="en-sub">{c['en']}</span></h3>
                        <p>{c['description']}</p>
                        <a href="javascript:void(0)" onclick="initiateRelayGift('{c['id']}', '{c['url']}', '{c['en']}')" class="btn btn-primary">DIRECT GIFT</a>
                    </div>
'''
    return html

def update_campaigns_file():
    base_dir = r"c:\Users\gaelf\Documents\GitHub\local_ai_campaign_assistant"
    camp_path = os.path.join(base_dir, 'frontend', 'campaigns.html')
    
    with open(camp_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    campaigns = get_full_campaign_data()
    cards_html = generate_cards_html(campaigns)
    
    # Replace the container content
    # Looking for the cards-grid and its end
    # Robust replacement using split
    start_marker = '<div class="cards-grid" id="campaign-list-container">'
    end_marker = '<!-- END CAMPAIGNS -->'
    
    if start_marker in content and end_marker in content:
        parts = content.split(start_marker)
        head = parts[0] + start_marker
        tail_parts = parts[1].split(end_marker)
        tail = end_marker + tail_parts[1]
        new_content = head + cards_html + tail
    else:
        # Fallback to the pattern but make it more flexible
        pattern = re.compile(r'(<div class="cards-grid" id="campaign-list-container">)(.*?)(</div>\s*</div>)', re.DOTALL)
        new_content = pattern.sub(r'\1' + cards_html + r'\3', content)
    
    # Increase main padding-top to prevent logo overlap
    new_content = re.sub(
        r'<main style="padding-top: \d+px;">',
        '<main style="padding-top: 220px;">',
        new_content
    )
    
    with open(camp_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"Successfully populated {len(campaigns)} campaigns in campaigns.html with sorting and full content.")

if __name__ == "__main__":
    update_campaigns_file()
