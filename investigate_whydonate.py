import requests
import re

login_url = "https://whydonate.com/en/login/"
try:
    response = requests.get(login_url)
    print(f"Status Code: {response.status_code}")
    # Look for common login form indicators
    action = re.findall(r'action="([^"]+)"', response.text)
    print(f"Form Action: {action}")
    
    # Also check for CSRF tokens or similar
    csrf = re.findall(r'name="csrfmiddlewaretoken" value="([^"]+)"', response.text)
    print(f"CSRF: {csrf}")
    
    # Check for API-like scripts
    scripts = re.findall(r'src="([^"]+)"', response.text)
    for s in scripts:
        if "main" in s or "app" in s:
            print(f"Script: {s}")

except Exception as e:
    print(f"Error: {e}")
