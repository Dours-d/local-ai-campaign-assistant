import requests
import json

URL = "http://127.0.0.1:5010/api/submissions/972592475288"

def verify_api():
    try:
        resp = requests.get(URL)
        if resp.status_code != 200:
            print(f"API Error: {resp.status_code}")
            return
        
        data = resp.json()
        print(f"Total submission records: {len(data)}")
        
        for i, sub in enumerate(data):
            imgs = sub.get('images', [])
            print(f"Record {i} | BID: {sub.get('bid')} | Images: {len(imgs)}")
            if imgs:
                print(f"  First Image Sample: {imgs[0][:60]}...")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    verify_api()
