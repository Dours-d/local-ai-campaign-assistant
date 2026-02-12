
import os
import json
from datetime import datetime

SUBMISSIONS_DIR = 'data/onboarding_submissions'
BENEFICIARIES_FILE = 'data/potential_beneficiaries.json'

def get_all_submissions():
    subs = []
    if not os.path.exists(SUBMISSIONS_DIR): return subs
    for f in os.listdir(SUBMISSIONS_DIR):
        if f.endswith('.json'):
            path = os.path.join(SUBMISSIONS_DIR, f)
            try:
                with open(path, 'r', encoding='utf-8') as jf:
                    data = json.load(jf)
                    subs.append({
                        'file': f, 
                        'id': str(data.get('beneficiary_id', '')), 
                        'name': data.get('display_name', ''),
                        'whatsapp': data.get('whatsapp_number', '')
                    })
            except: pass
    return subs

# Load beneficiaries
try:
    with open(BENEFICIARIES_FILE, 'r', encoding='utf-8') as f:
        beneficiaries = json.load(f)
except Exception as e:
    print(f"Error loading beneficiaries: {e}")
    beneficiaries = []

all_subs = get_all_submissions()

print(f"--- RECONCILIATION SUMMARY ---")
print(f"Total Targeted Beneficiaries: {len(beneficiaries)}")
print(f"Total Submissions Found: {len(all_subs)}")

print(f"\n--- MATCHES (Targeted who have submitted) ---")
matched_names = []
for b in beneficiaries:
    b_name = b['name']
    # Try to match by name or by numeric ID
    clean_id = ''.join(filter(str.isdigit, b_name))
    
    found = False
    for s in all_subs:
        # Match by ID string (e.g. 'viral_97259...' or '96778...')
        if clean_id and clean_id in s['id']:
            found = True
        # Match by exact name if it is a text-ID
        if b_name == s['id'] or b_name == s['name']:
            found = True
            
        if found:
            print(f"✅ Match: {b_name} matched with submission {s['file']}")
            matched_names.append(b_name)
            break

print(f"\n--- NON-NUMERIC IDS CHECK ---")
text_ids = [b['name'] for b in beneficiaries if not any(c.isdigit() for c in b['name'])]
for tid in text_ids:
    has_data = any(tid in s['id'] or tid in s['name'] for s in all_subs)
    status = "DATA FOUND" if has_data else "NO DATA"
    print(f"- {tid}: {status}")

missing_count = len(beneficiaries) - len(matched_names)
print(f"\nTotal Missing: {missing_count}")
