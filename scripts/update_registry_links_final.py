import json

REGISTRY_PATH = 'data/campaign_registry.json'

WORKING_LINKS = {
    "972597341113": "https://whydonate.com/fundraising/help-akram-and-his-family-survive-and-find-stability-in-gaza", # Verified LIVE in audit
    "972598827480": "https://whydonate.com/fundraising/elp-magda-and-muhammad-rebuild-after-the-destruction-in-gaza", # USER FORCED
    "972597662819": "https://whydonate.com/fundraising/help-fatima-yasser-her-5-children-survive-starvation-in-gaza-palestine", # Found by search
    "972599904464": "https://whydonate.com/fundraising/-help-me-rebuild-my-home", # DASH REQUIRED
    "972592115058": "https://whydonate.com/fundraising/-urgent-winter-aid-for-mother-of-10", # DASH REQUIRED
    "972567243079": "https://whydonate.com/fundraising/-a-tent-of-hope-rebuilding-our-lives", # DASH REQUIRED
    "972567419045": "https://whydonate.com/fundraising/-emergency-shelter-help-us-buy-a-tent", # DASH REQUIRED
    "972595562213": "https://whydonate.com/fundraising/urgent-medical-aid-for-my-child-and-husband", # Verified LIVE
    "972592645759": "https://whydonate.com/fundraising/help-raneen-al-quraan-and-her-family-find-shelter-in-gaza", # Verified LIVE
    "972599560696": "https://whydonate.com/fundraising/help-mohammed-pursue-dentistry-and-support-his-family", # Verified LIVE
    "972598289338": "https://whydonate.com/fundraising/urgent-support-for-pregnant-mother-and-family" # Verified LIVE
}

def update_registry():
    with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    mappings = data.get('mappings', {})
    updated = 0
    
    for bid, url in WORKING_LINKS.items():
        if bid in mappings:
            old_url = mappings[bid].get('whydonate_url')
            if old_url != url:
                mappings[bid]['whydonate_url'] = url
                print(f"Updated {bid}: {old_url} -> {url}")
                updated += 1
    
    if updated > 0:
        with open(REGISTRY_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Total updated: {updated}")
    else:
        print("No updates needed.")

if __name__ == "__main__":
    update_registry()
