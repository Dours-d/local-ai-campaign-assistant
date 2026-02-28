import os
import re

def inject_relay(html_path):
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Create regex to find WhyDonate buttons in cards
    # Pattern: <a href="[URL]" class="btn btn-primary" target="_blank">DIRECT GIFT</a>
    # We want to replace it with: <a href="javascript:void(0)" onclick="initiateRelayGift('[ID]', '[URL]', '[NAME]')" class="btn btn-primary">DIRECT GIFT</a>
    
    # First, let's find the card structures to get names
    card_pattern = re.compile(r'(<div class="card"[^>]*>.*?<span class="en-sub">([^<]+)</span>.*?<a href="(https://whydonate.com/fundraising/[^"]+)"[^>]*>DIRECT GIFT</a>)', re.DOTALL)
    
    def replacer(match):
        full_card_content = match.group(1)
        display_name = match.group(2).strip().replace('\n', ' ').replace('  ', ' ')
        primary_url = match.group(3)
        
        # Create a safe ID
        safe_id = re.sub(r'\W+', '_', display_name).lower()
        
        # New button
        new_btn = f'onclick="initiateRelayGift(\'{safe_id}\', \'{primary_url}\', \'{display_name}\')" class="btn btn-primary">DIRECT GIFT</a>'
        
        # Find the original link within the match
        old_link_pattern = re.compile(r'<a href="https://whydonate.com/fundraising/[^"]+"[^>]*>DIRECT GIFT</a>')
        return old_link_pattern.sub(f'<a href="javascript:void(0)" {new_btn}', full_card_content)

    new_content = card_pattern.sub(replacer, content)
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"Relay logic injected into {html_path}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    html_file = os.path.join(base_dir, 'frontend', 'campaigns.html')
    inject_relay(html_file)
