import shutil
import os

src = r"C:\Users\gaelf\Pictures\GAZA\Fajr\g871-transparency-floor.png"
dst = r"c:\Users\gaelf\Documents\GitHub\local_ai_campaign_assistant\frontend\images\g871-transparency-floor.png"

try:
    shutil.copy2(src, dst)
    print(f"Successfully copied {src} to {dst}")
except Exception as e:
    print(f"Error: {e}")
