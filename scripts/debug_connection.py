
import requests
try:
    print("Checking Chrome connection...")
    resp = requests.get("http://127.0.0.1:9222/json")
    print(f"Status: {resp.status_code}")
    print(f"Content: {resp.text}")
except Exception as e:
    print(f"Failed: {e}")
