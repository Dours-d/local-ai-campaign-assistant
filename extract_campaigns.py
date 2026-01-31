import requests
from bs4 import BeautifulSoup
import json

session = requests.Session()
login_url = "https://whydonate.com/wp-login.php"
dashboard_url = "https://whydonate.com/en/dashboard/" # Guessing common path

payload = {
    'log': 'gael.fichet@gmail.com',
    'pwd': 'Whydonate@gael1',
    'wp-submit': 'Log In',
    'redirect_to': dashboard_url,
    'testcookie': 1
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

try:
    print("Attempting login...")
    response = session.post(login_url, data=payload, headers=headers, allow_redirects=True)
    print(f"Final URL: {response.url}")
    print(f"Status Code: {response.status_code}")
    
    if "dashboard" in response.url or response.status_code == 200:
        print("Login seems successful or redirected.")
        
        # Now try to find campaign data. 
        # Often fundraisers are listed in a JSON blob or a specific table.
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for script tags containing 'fundraiser' or 'campaign'
        campaigns = []
        for script in soup.find_all('script'):
            if script.string and ('fundraiser' in script.string or 'campaign' in script.string):
                # This might contain a JSON blob
                print("Found potential campaign data in script tag.")
                # print(script.string[:500]) # Don't print everything
        
        # Try a more direct fundraiser list URL if known
        fundraisers_url = "https://whydonate.com/en/dashboard/fundraisers/"
        print(f"Checking {fundraisers_url}...")
        res_f = session.get(fundraisers_url, headers=headers)
        print(f"Fundraisers Page Status: {res_f.status_code}")
        
        # Save HTML for inspection if needed
        with open("dashboard_sample.html", "w", encoding='utf-8') as f:
            f.write(res_f.text)
            
except Exception as e:
    print(f"Error: {e}")
