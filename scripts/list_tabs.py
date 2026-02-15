import requests, json
try:
    r = requests.get("http://127.0.0.1:9222/json")
    tabs = r.json()
    for t in tabs:
        print(f"Type: {t.get('type')} | Title: {t.get('title')} | URL: {t.get('url')}")
except Exception as e:
    print(f"Error: {e}")
