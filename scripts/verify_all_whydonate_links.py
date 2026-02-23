import json
import requests
import time

def check_links():
    with open('campaign_index_full.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    results = []
    for phone, entry in data.items():
        if 'whydonate' in entry and 'url' in entry['whydonate']:
            url = entry['whydonate']['url']
            try:
                # Using a small delay to avoid rate limiting
                time.sleep(1.0)
                # GET request to fully follow redirects (including some server-side logic)
                response = requests.get(url, timeout=15, allow_redirects=True)
                status = response.status_code
                final_url = response.url.lower()
                
                # Check for "not-found" in the final URL which indicates a false positive 200
                if "not-found" in final_url or "fundraiser-not-found" in final_url:
                    results.append(f"Phone: {phone} | URL: {url} | REDIRECTED TO: {response.url} (404/NOT FOUND)")
                elif status != 200:
                    results.append(f"Phone: {phone} | URL: {url} | Status: {status}")
            except Exception as e:
                results.append(f"Phone: {phone} | URL: {url} | Error: {str(e)}")
    
    if results:
        print("\n".join(results))
    else:
        print("All WhyDonate links are reachable (200 OK).")

if __name__ == "__main__":
    check_links()
