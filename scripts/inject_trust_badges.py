import os
import re

def inject_trust_badges(html_path):
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern to find cards and extract the campaign name from the en-sub span
    # We want to insert the badge before the <h3>
    card_regex = re.compile(r'(<div class="card"[^>]*>)(.*?)(<h3[^>]*>.*?<span class="en-sub">([^<]+)</span>.*?</h3>)', re.DOTALL)

    def replacer(match):
        open_div = match.group(1)
        inner_pre_h3 = match.group(2)
        h3_block = match.group(3)
        display_name = match.group(4).strip().replace('\n', ' ').replace('  ', ' ')
        
        # Generate the same safe ID used in the relay calls (strip relay call if already exists)
        safe_id = re.sub(r'\W+', '_', display_name).lower().strip('_')
        
        # Avoid duplicate badges
        if 'card-status' in match.group(0):
            return match.group(0)
            
        badge_html = f'\n                        <div class="card-status" data-campaign-id="{safe_id}"><span class="status-dot active"></span> TRUST VERIFIED</div>'
        
        return f"{open_div}{inner_pre_h3}{badge_html}{h3_block}"

    new_content = card_regex.sub(replacer, content)
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"Trust badges successfully injected into {html_path}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    html_file = os.path.join(base_dir, 'frontend', 'campaigns.html')
    inject_trust_badges(html_file)
