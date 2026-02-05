import os
import json
import time
import subprocess
import logging
from datetime import datetime

# Paths
SUBMISSIONS_DIR = "data/onboarding_submissions"
INDEX_FILE = "data/campaign_index.json"
LOG_FILE = "logs/watch_onboarding.log"

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

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

def save_index(index):
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2)

from whydonate_automater import create_single_whydonate

def process_new_submission(file_path):
    logging.info(f"Processing new submission: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        whatsapp = format_whatsapp(data.get('whatsapp_number'))
        if not whatsapp:
            logging.error(f"No WhatsApp number found in {file_path}")
            return

        index = load_index()
        if whatsapp not in index:
            index[whatsapp] = {}
        
        entry = index[whatsapp]
        campaign_data = {
            "title": data.get('title'),
            "description": data.get('story'),
            "story": data.get('story'),
            "image": data.get('files', [{}])[0].get('path') if data.get('files') else None
        }
        
        # 1. Create on Whydonate if not exists
        if 'whydonate' not in entry:
            logging.info(f"Triggering Whydonate creation for {whatsapp}")
            success = create_single_whydonate(campaign_data)
            if success:
                entry['whydonate'] = {"status": "created", "timestamp": datetime.now().isoformat()}
                logging.info(f"SUCCESS: Whydonate created for {whatsapp}")
            else:
                logging.error(f"FAILURE: Whydonate creation failed for {whatsapp}")
        
        save_index(index)
        
    except Exception as e:
        logging.error(f"Error processing {file_path}: {e}")

def main():
    logging.info("Starting Onboarding Watchdog...")
    processed_files = set()
    
    # Initial scan: process anything that isn't in index yet
    index = load_index()
    for f in os.listdir(SUBMISSIONS_DIR):
        if f.endswith(".json") and "submission" in f:
            file_path = os.path.join(SUBMISSIONS_DIR, f)
            try:
                with open(file_path, 'r', encoding='utf-8') as sf:
                    data = json.load(sf)
                whatsapp = format_whatsapp(data.get('whatsapp_number'))
                if whatsapp and whatsapp not in index:
                    logging.info(f"Unindexed file found in initial scan: {f}")
                    process_new_submission(file_path)
                    index = load_index() # Refresh index
            except: pass
            processed_files.add(f)
    
    while True:
        try:
            current_files = set(f for f in os.listdir(SUBMISSIONS_DIR) if f.endswith(".json") and "submission" in f)
            new_files = current_files - processed_files
            
            for f in new_files:
                process_new_submission(os.path.join(SUBMISSIONS_DIR, f))
                processed_files.add(f)
            
            time.sleep(10)
        except KeyboardInterrupt:
            break
        except Exception as e:
            logging.error(f"Watchdog Loop Error: {e}")
            time.sleep(30)

if __name__ == "__main__":
    main()
