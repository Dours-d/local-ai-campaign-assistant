import requests
import os

url = "http://127.0.0.1:5010"
password = "admin123"
video_path = r"c:\Users\gaelf\Documents\GitHub\local_ai_campaign_assistant\vault\amplification\pulse_verticals\D1_Gaza_Family_vertical.mp4"

session = requests.Session()
# Login
print("Logging in...")
r = session.post(f"{url}/login", json={"password": password})
print(f"Login Response: {r.status_code}, {r.json()}")

# Upload
print(f"Uploading {video_path}...")
with open(video_path, 'rb') as f:
    files = {'file': (os.path.basename(video_path), f, 'video/mp4')}
    r = session.post(f"{url}/api/publish-pulse", files=files)
    print(f"Upload Response: {r.status_code}, {r.json()}")
