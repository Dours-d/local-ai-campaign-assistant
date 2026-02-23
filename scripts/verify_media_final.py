import requests
import os

SUBMISSION_ID = "972592475288"
API_URL = f"http://127.0.0.1:5010/api/submissions/{SUBMISSION_ID}"

def verify():
    print(f"Fetching submissions for {SUBMISSION_ID}...")
    r = requests.get(API_URL)
    if r.status_code != 200:
        print(f"API Error: {r.status_code}")
        return
    
    data = r.json()
    # Find record with images
    target = next((s for s in data if s.get('image_urls')), None)
    if not target:
        print("No record with image_urls found.")
        return
    
    url = target['image_urls'][0]
    path = target['local_paths'][0]
    print(f"Found Image URL: {url}")
    print(f"Found Local Path: {path}")
    
    media_url = f"http://127.0.0.1:5010{url}"
    print(f"Testing media fetch from {media_url}...")
    r_media = requests.get(media_url)
    print(f"Media Fetch Status: {r_media.status_code}")
    if r_media.status_code == 200:
        print(f"Success! Content type: {r_media.headers.get('Content-Type')}")
        print(f"Content length: {len(r_media.content)} bytes")

if __name__ == "__main__":
    verify()
