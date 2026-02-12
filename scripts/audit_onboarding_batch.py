import os
import json
import sys

# Ensure UTF-8 output even on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SUBMISSIONS_DIR = "data/onboarding_submissions"
INDEX_FILE = "data/campaign_index.json"

def format_whatsapp(num):
    if not num: return None
    num = "".join([c for c in str(num) if c.isdigit()])
    if not num: return None
    if not num.startswith("+"):
        num = "+" + num
    return num

def load_index():
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def audit():
    index = load_index()
    submissions = [f for f in os.listdir(SUBMISSIONS_DIR) if f.endswith(".json") and "submission" in f]
    
    print(f"Total submission files: {len(submissions)}")
    print("-" * 50)
    
    pending = []
    
    for f in submissions:
        path = os.path.join(SUBMISSIONS_DIR, f)
        try:
            with open(path, 'r', encoding='utf-8') as sf:
                data = json.load(sf)
            
            whatsapp = format_whatsapp(data.get('whatsapp_number'))
            beneficiary_id = data.get('beneficiary_id', '')
            
            # If whatsapp is missing in field, try to extract from ID if it looks like a number
            if not whatsapp and beneficiary_id:
                potential_wa = format_whatsapp(beneficiary_id)
                if potential_wa and len(potential_wa) >= 8: # Arbitrary length check
                    whatsapp = potential_wa

            # Quality check
            story = data.get('story', '')
            has_media = len(data.get('files', [])) > 0
            is_complete = len(story) > 10 or has_media
            
            quality = "High" if is_complete else "Low"
            displayName = data.get('display_name', 'Unknown')

            # Key check: if whatsapp is provided, check index
            if whatsapp:
                if whatsapp not in index:
                    print(f"[{quality}] MISSING | WA: {whatsapp} | Name: {displayName} | File: {f}")
                    if is_complete: pending.append(path)
                elif 'whydonate' not in index[whatsapp]:
                    print(f"[{quality}] PENDING | WA: {whatsapp} | Name: {displayName} | File: {f}")
                    if is_complete: pending.append(path)
                else:
                    whydonate = index[whatsapp].get('whydonate', {})
                    if isinstance(whydonate, dict) and whydonate.get('status') == 'failed':
                        print(f"[{quality}] FAILED PREV | WA: {whatsapp} | Name: {displayName} | File: {f}")
                        if is_complete: pending.append(path)
            else:
                # Handle anonymous or viral ones without WhatsApp
                print(f"[{quality}] ANON/NO_WA | ID: {beneficiary_id} | Name: {displayName} | File: {f}")
                if beneficiary_id not in index and is_complete:
                    pending.append(path)
                
        except Exception as e:
            print(f"[ERROR] Reading {f}: {e}")

    print("-" * 50)
    print(f"Total pending to process (High Quality): {len(pending)}")
    return pending

if __name__ == "__main__":
    audit()

if __name__ == "__main__":
    audit()
