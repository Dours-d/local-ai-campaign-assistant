import requests
import json

session = requests.Session()
login_url = "https://whydonate.com/wp-login.php"
payload = {
    'log': 'gael.fichet@gmail.com',
    'pwd': 'Whydonate@gael1',
    'wp-submit': 'Log In',
    'testcookie': 1
}
headers = {'User-Agent': 'Mozilla/5.0'}

try:
    print("Logging in...")
    session.post(login_url, data=payload, headers=headers)
    
    # Try common JSON endpoints
    endpoints = [
        "https://whydonate.com/wp-json/whydonate/v1/fundraisers",
        "https://whydonate.com/wp-json/whydonate/v1/me/fundraisers",
        "https://whydonate.com/api/v1/fundraisers/me",
        "https://whydonate.com/en/api/fundraiser/list"
    ]
    
    for url in endpoints:
        print(f"Testing {url}...")
        r = session.get(url, headers=headers)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            try:
                data = r.json()
                print(f"SUCCESS! Found data in {url}")
                with open("campaigns_imported.json", "w") as f:
                    json.dump(data, f, indent=2)
                break
            except:
                print("Not JSON")

except Exception as e:
    print(f"Error: {e}")
