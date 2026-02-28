from bs4 import BeautifulSoup
import os

base_dir = r"c:\Users\gaelf\Documents\GitHub\local_ai_campaign_assistant"
html_path = os.path.join(base_dir, 'frontend', 'campaigns.html')

with open(html_path, 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f, 'html.parser')

cards = soup.select('.card')
print(f"Found {len(cards)} cards")

for i, card in enumerate(cards[:5]):
    btn = card.select_one('.btn-primary')
    print(f"Card {i} button: {btn}")
    if btn and btn.has_attr('onclick'):
        print(f"  onclick: {btn['onclick']}")
