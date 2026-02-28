import json
import os
import re

def slugify(text):
    return re.sub(r'\W+', '_', text.strip()).lower().strip('_')

def get_full_campaign_data():
    base_dir = r"c:\Users\gaelf\Documents\GitHub\local_ai_campaign_assistant"
    registry_path = os.path.join(base_dir, 'vault', 'UNIFIED_REGISTRY.json')
    
    with open(registry_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Filter for items with a whydonate_url and identity_name
    campaigns = []
    seen_urls = set()
    
    # Priority: Abdullah Hoping first
    abdullah = None
    for entry in data:
        name = entry.get('identity_name', 'Unknown')
        url = entry.get('whydonate_url')
        if not url or url in seen_urls: continue
        seen_urls.add(url)
        
        # Clean up title: remove everything after the first "|" or "-" to keep it clean
        raw_title = entry.get('title', name)
        clean_title = re.split(r'[|\-]', raw_title)[0].strip()
        
        # Split title into AR/EN if possible, or just use identity name
        # Some are like "Help Abdullah Hoping | ساعد عبد الله"
        # We want the bilingual structure. 
        # For simplicity, if we have a bilingual title, we'll try to extract it
        ar_title = ""
        en_title = clean_title
        
        if any('\u0600' <= c <= '\u06FF' for c in raw_title):
            # Try to extract the AR part
            ar_matches = re.findall(r'[\u0600-\u06FF\s]+', raw_title)
            if ar_matches:
                ar_title = " ".join(ar_matches).strip()
            
        # Truncate description
        desc = entry.get('description', '')
        if '---' in desc: desc = desc.split('---')[0].strip() # Take EN part
        desc = desc[:150] + "..." if len(desc) > 150 else desc
        
        c_data = {
            "id": slugify(name),
            "name": name,
            "ar": ar_title or name, # Fallback
            "en": en_title,
            "description": desc,
            "url": url
        }
        
        if "abdullah" in name.lower() and "hoping" in name.lower():
            abdullah = c_data
        else:
            campaigns.append(c_data)
            
    # Sort others by name or just as they come
    if abdullah:
        return [abdullah] + campaigns
    return campaigns

def generate_cards_html(campaigns):
    html = ""
    for i, c in enumerate(campaigns):
        delay = (i % 3) * 100
        html += f'''
                    <!-- {c['name']} -->
                    <div class="card" data-aos="fade-up" data-aos-delay="{delay}">
                        <div class="card-status" data-campaign-id="{c['id']}"><span class="status-dot active"></span> TRUST VERIFIED</div>
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
    pattern = re.compile(r'(<div class="cards-grid" id="campaign-list-container">)(.*?)(</div>\s*<!-- Pagination or footer -->)', re.DOTALL)
    
    # If the second part isn't exactly there, try a simpler replacement
    # Looking for the cards-grid and its end
    pattern = re.compile(r'(<div class="cards-grid" id="campaign-list-container">)(.*?)(</div>\s*</div>\s*</section>)', re.DOTALL)
    
    new_content = pattern.sub(r'\1' + cards_html + r'\3', content)
    
    with open(camp_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"Successfully populated {len(campaigns)} campaigns in campaigns.html")

if __name__ == "__main__":
    update_campaigns_file()
