import re
import requests
import time

def audit_messages():
    with open('onboarding_messages.txt', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Regex to find WhyDonate fundraising links
    links = re.findall(r'https?://(?:www\.)?whydonate\.com/fundraising/([a-zA-Z0-9-]+)', content)
    unique_links = sorted(list(set(links)))
    
    print(f"Found {len(unique_links)} unique WhyDonate slugs in onboarding_messages.txt\n")
    
    broken_links = []
    
    for slug in unique_links:
        url = f"https://whydonate.com/fundraising/{slug}"
        try:
            time.sleep(1.0) # Respectful delay
            print(f"Probing: {url}...", end="\r")
            response = requests.get(url, timeout=15, allow_redirects=True)
            final_url = response.url.lower()
            
            # Check for illusion (200 OK but redirected to not-found)
            if "not-found" in final_url or "fundraiser-not-found" in final_url:
                broken_links.append(f"BROKEN: {url} -> Redirected to {response.url}")
            elif response.status_code != 200:
                broken_links.append(f"BROKEN: {url} -> Status {response.status_code}")
                
        except Exception as e:
            broken_links.append(f"ERROR: {url} -> {str(e)}")

    print("\n" + "="*50)
    if broken_links:
        print("AUDIT FAILURE: Broken links found in onboarding_messages.txt:")
        print("\n".join(broken_links))
        
        # Check specifically for the hyphen issue
        potential_hyphen_fixes = []
        for bl in broken_links:
            if "whydonate.com/fundraising/" in bl:
                slug = bl.split("whydonate.com/fundraising/")[1].split(" ")[0]
                # Test if adding a hyphen fixes it
                url_with_hyphen = f"https://whydonate.com/fundraising/{slug}-"
                try:
                    resp = requests.get(url_with_hyphen, timeout=10, allow_redirects=True)
                    if "not-found" not in resp.url.lower() and resp.status_code == 200:
                        potential_hyphen_fixes.append(f"FIX FOUND: {slug} -> {slug}-")
                except:
                    pass
        
        if potential_hyphen_fixes:
            print("\nSUGGESTED SYSTEMIC FIXES (Hyphen missing):")
            print("\n".join(potential_hyphen_fixes))
    else:
        print("AUDIT SUCCESS: All links in onboarding_messages.txt are alive.")

if __name__ == "__main__":
    audit_messages()
