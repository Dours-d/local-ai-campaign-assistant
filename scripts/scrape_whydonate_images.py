import json
import os
import requests
import re
import time
from pathlib import Path

# Paths
REGISTRY_PATH = 'vault/UNIFIED_REGISTRY.json'
MEDIA_DIR = Path('data/onboarding_submissions/media/scraped_whydonate')
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def scrape_images():
    if not os.path.exists(REGISTRY_PATH):
        print(f"Error: Registry not found at {REGISTRY_PATH}")
        return

    if not MEDIA_DIR.exists():
        MEDIA_DIR.mkdir(parents=True, exist_ok=True)

    with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
        registry = json.load(f)

    updated_count = 0
    total_missing = sum(1 for c in registry if c.get('whydonate_url') and not c.get('image'))
    print(f"Starting scrape for {total_missing} campaigns...")

    for i, campaign in enumerate(registry):
        url = campaign.get('whydonate_url')
        image = campaign.get('image')

        if url and not image:
            print(f"[{i+1}/{len(registry)}] Processing: {url}")
            try:
                resp = requests.get(url, headers=HEADERS, timeout=15)
                if resp.status_code != 200:
                    print(f"  ✗ Failed to load page: {resp.status_code}")
                    continue

                # Look for campaign image in HTML
                match = re.search(r'https://whydonate.com/cdn-cgi/imagedelivery/[^"]*fundraiser_header[^"]*', resp.text)
                if not match:
                    # Generic pattern
                    match = re.search(r'https://whydonate.com/cdn-cgi/imagedelivery/[^"]+', resp.text)
                
                if match:
                    img_url = match.group(0)
                    print(f"  ✓ Found Image URL: {img_url}")
                    
                    # Clean up URL (sometimes has trailing query params)
                    clean_img_url = img_url.split('?')[0]
                    # Usually "public" is the variant
                    if not clean_img_url.endswith('/public'):
                         if '/fundraiser_header/' in clean_img_url:
                              clean_img_url = clean_img_url.split('/fundraiser_header/')[0] + '/fundraiser_header/' + clean_img_url.split('/fundraiser_header/')[1].split('/')[0] + '/public'

                    # Download
                    slug = url.split('/')[-1] if url.split('/')[-1] else f"img_{i}"
                    ext = ".jpg" # Default
                    img_path = MEDIA_DIR / f"{slug}{ext}"
                    
                    img_resp = requests.get(img_url, headers=HEADERS, timeout=15)
                    if img_resp.status_code == 200:
                        with open(img_path, 'wb') as f_img:
                            f_img.write(img_resp.content)
                        
                        campaign['image'] = str(img_path.absolute())
                        updated_count += 1
                        print(f"  ✓ Saved to: {img_path}")
                    else:
                        print(f"  ✗ Failed to download image: {img_resp.status_code}")
                else:
                    print("  ✗ No image found in HTML")

                # Politely wait
                time.sleep(1)

            except Exception as e:
                print(f"  ✗ Error: {e}")

    if updated_count > 0:
        with open(REGISTRY_PATH, 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=4, ensure_ascii=False)
        print(f"\n✅ Successfully updated {updated_count} campaigns with WhyDonate visuals.")
    else:
        print("\nNo campaigns were updated.")

if __name__ == "__main__":
    scrape_images()
