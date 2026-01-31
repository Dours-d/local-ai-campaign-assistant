import requests
from bs4 import BeautifulSoup

url = "https://whydonate.com/en/profile/gael-cedric-fichet/"
headers = {'User-Agent': 'Mozilla/5.0'}

try:
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # In Angular apps, data is often in a script tag as a JSON
    # Or it might be in the text if it's SSR
    print(f"Status: {r.status_code}")
    
    # Search for titles we know exist
    titles = ["Hamza", "Aya", "Wafaa", "Mahmoud", "Ibtisam"]
    for t in titles:
        if t in r.text:
            print(f"Found mention of {t}")
            
    # Try to find links to fundraising pages
    links = [a.get('href') for a in soup.find_all('a') if a.get('href') and '/fundraising/' in a.get('href')]
    print(f"Fundraising links found: {len(links)}")
    for l in links[:5]:
        print(f" - {l}")

except Exception as e:
    print(f"Error: {e}")
