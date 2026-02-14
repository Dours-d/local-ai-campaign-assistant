import requests
import json

CDP_URL = "http://127.0.0.1:9222/json"

try:
    r = requests.get(CDP_URL).json()
    for t in r:
        print(f"ID: {t.get('id')}")
        print(f"Type: {t.get('type')}")
        print(f"Title: {t.get('title')}")
        print(f"URL: {t.get('url')}")
        print("-" * 20)
except Exception as e:
    print(f"Error: {e}")
