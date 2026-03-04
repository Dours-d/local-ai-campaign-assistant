import re
from pathlib import Path

html_path = 'frontend/campaigns.html'

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Pattern to find a card and its whydonate URL
# We split the html by generic image tags, then look ahead to find the URL
cards = re.split(r'(<div class=\"card\"[^>]*>)', html)
new_html = cards[0]

for i in range(1, len(cards), 2):
    card_open = cards[i]
    card_content = cards[i+1]
    
    # Check if there is a whydonate url in this card
    url_match = re.search(r'https://whydonate.com/fundraising/([^\"\'\,\)]+)', card_content)
    if url_match:
        slug = url_match.group(1).rstrip('/')
        img_src = f'../data/onboarding_submissions/media/scraped_whydonate/{slug}.jpg'
        
        # Replace ONLY generic images
        card_content = re.sub(r'<img src=\"images/[^\"]+\"', f'<img src=\"{img_src}\"', card_content)
            
    new_html += card_open + card_content

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(new_html)

print('Successfully mapped all remaining WhyDonate campaign images.')
