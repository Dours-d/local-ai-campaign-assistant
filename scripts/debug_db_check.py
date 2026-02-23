import sqlite3
import json
import os

DB_PATH = 'vault/submissions.db' if os.path.exists('vault') else 'data/submissions.db'
SEARCH_ID = "972592475288"

def debug_query():
    print(f"Checking DB: {DB_PATH}")
    if not os.path.exists(DB_PATH):
        print("DB not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Try multiple match patterns
    cursor.execute("SELECT bid, whatsapp, media_json FROM submissions WHERE bid LIKE ? OR whatsapp LIKE ?", (f"%{SEARCH_ID}%", f"%{SEARCH_ID}%"))
    rows = cursor.fetchall()
    
    if not rows:
        print(f"No records found for {SEARCH_ID}")
    else:
        for bid, wa, media in rows:
            print(f"Match Found: bid={bid}, whatsapp={wa}")
            data = json.loads(media)
            print(f"Number of images: {len(data)}")
            for idx, img in enumerate(data):
                print(f"Image {idx} sample: {str(img)[:100]}...")
    
    conn.close()

if __name__ == "__main__":
    debug_query()
