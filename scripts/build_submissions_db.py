import os
import json
import sqlite3
import base64
import mimetypes

# Base directory setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VAULT_DIR = os.path.join(BASE_DIR, 'vault')
DATA_ROOT = os.path.join(BASE_DIR, 'data')

# Detection Logic (Vault-first)
IS_PRIVATE = os.path.exists(VAULT_DIR)
ACTIVE_ROOT = VAULT_DIR if IS_PRIVATE else DATA_ROOT
DB_PATH = os.path.join(ACTIVE_ROOT, 'submissions.db')
ONBOARDING_DIR = os.path.join(ACTIVE_ROOT, "onboarding_submissions")
MEDIA_DIR = os.path.join(ONBOARDING_DIR, "media")

import requests

def image_to_base64(target):
    """Convert an image file or URL to a data URL (Base64)."""
    if not target:
        return None
    try:
        # 1. Handle Remote URLs (Harvesting)
        if str(target).startswith('http'):
            print(f"  [HARVEST] Fetching {target}...")
            resp = requests.get(target, timeout=10)
            if resp.status_code == 200:
                content_type = resp.headers.get('Content-Type', 'image/jpeg')
                encoded_string = base64.b64encode(resp.content).decode('utf-8')
                return f"data:{content_type};base64,{encoded_string}"
            return None

        # 2. Handle Local Files
        if not os.path.exists(target):
            return None
        
        mime_type, _ = mimetypes.guess_type(target)
        if not mime_type:
            mime_type = "image/jpeg"
        with open(target, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return f"data:{mime_type};base64,{encoded_string}"
    except Exception as e:
        print(f"  [ERR] Failed to encode {target}: {e}")
        return None

def build_db():
    print(f"--- Establishing Formal SQLite Database (Confidential Mode) ---")
    print(f"Active Root: {ACTIVE_ROOT}")
    
    # Connect and setup schema
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS submissions")
    cursor.execute("""
        CREATE TABLE submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bid TEXT,
            whatsapp TEXT,
            title TEXT,
            story TEXT,
            media_json TEXT,
            media_paths_json TEXT
        )
    """)
    
    matches = []
    
    # 1. Load from extracted_real_submissions.json
    potential_json_paths = [
        os.path.join(VAULT_DIR, 'extracted_real_submissions.json'),
        os.path.join(DATA_ROOT, 'extracted_real_submissions.json')
    ]
    for pjson in potential_json_paths:
        if os.path.exists(pjson):
            print(f"Loading metadata from {pjson}...")
            try:
                with open(pjson, 'r', encoding='utf-8') as f:
                    raw = json.load(f)
                matches.extend(raw if isinstance(raw, list) else [])
            except Exception as e:
                print(f"  [WARN] Failed to read {pjson}: {e}")

    # 2. Add individual submission files
    if os.path.isdir(ONBOARDING_DIR):
        print(f"Scanning individual submission files in {ONBOARDING_DIR}...")
        for fname in os.listdir(ONBOARDING_DIR):
            if fname.endswith('_submission.json'):
                try:
                    with open(os.path.join(ONBOARDING_DIR, fname), 'r', encoding='utf-8') as f:
                        matches.append(json.load(f))
                except Exception:
                    pass

    print(f"Processing {len(matches)} potential records...")
    
    # 3. Process all candidates and deduplicate
    bid_to_best_record = {}
    
    for s in matches:
        bid = str(s.get('bid') or s.get('clean_id') or s.get('beneficiary_id'))
        whatsapp = str(s.get('whatsapp') or s.get('phone') or s.get('whatsapp_number') or bid)
        title = s.get('title', '')
        story = s.get('story', '')
        
        # Collect all potential image sources
        raw_sources = []
        if s.get('image'): raw_sources.append(s.get('image'))
        if s.get('images'): raw_sources.extend(s.get('images'))
        for f in s.get('files', []):
            if isinstance(f, dict) and f.get('path'): raw_sources.append(f.get('path'))
            elif isinstance(f, str): raw_sources.append(f)
        
        media_list = []
        paths_list = []
        for p in raw_sources:
            # 1. Handle Remote URLs (Harvesting)
            if str(p).startswith('http'):
                b64 = image_to_base64(p)
                if b64:
                    media_list.append(b64)
                    paths_list.append(str(p))
                continue

            # 2. Handle Local Files
            p_str = str(p).replace('\\', '/')
            rel_p = p_str
            for prefix in ['data/onboarding_submissions/media/', 'vault/onboarding_submissions/media/', 'media/']:
                if rel_p.startswith(prefix):
                    rel_p = rel_p[len(prefix):]
                    break
            
            pfp_list = [
                os.path.join(MEDIA_DIR, rel_p),
                os.path.join(ONBOARDING_DIR, rel_p),
                os.path.abspath(p_str)
            ]
            
            for pfp in pfp_list:
                if os.path.exists(pfp) and os.path.isfile(pfp):
                    b64 = image_to_base64(pfp)
                    if b64:
                        media_list.append(b64)
                        paths_list.append(pfp)
                        break
        
        # Scoring: record with more found paths is better
        score = len(paths_list)
        if bid not in bid_to_best_record or score > bid_to_best_record[bid]['score']:
            bid_to_best_record[bid] = {
                'data': (bid, whatsapp, title, story, json.dumps(media_list), json.dumps(paths_list)),
                'score': score
            }

    # 4. Insert into DB
    count = 0
    for bid in bid_to_best_record:
        cursor.execute("""
            INSERT INTO submissions (bid, whatsapp, title, story, media_json, media_paths_json)
            VALUES (?, ?, ?, ?, ?, ?)
        """, bid_to_best_record[bid]['data'])
        count += 1

    conn.commit()
    conn.close()
    
    size_mb = os.path.getsize(DB_PATH) / (1024 * 1024)
    print(f"--- Migration Complete ---")
    print(f"Database: {DB_PATH} ({size_mb:.2f} MB)")
    print(f"Total Records: {count}")

if __name__ == "__main__":
    build_db()
