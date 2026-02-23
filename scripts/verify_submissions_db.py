import sqlite3
import json
import os

DB_PATH = 'vault/submissions.db' if os.path.exists('vault') else 'data/submissions.db'

def verify():
    if not os.path.exists(DB_PATH):
        print(f"Error: {DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM submissions")
    print(f"Total Submissions: {cursor.fetchone()[0]}")

    cursor.execute("SELECT COUNT(*) FROM submissions WHERE media_json != '[]'")
    print(f"Submissions with Images: {cursor.fetchone()[0]}")

    cursor.execute("SELECT bid, title, length(media_json) as ml FROM submissions WHERE media_json != '[]' LIMIT 5")
    rows = cursor.fetchall()
    print("\nSample records with media:")
    for row in rows:
        print(f"  BID: {row['bid']} | Title: {row['title']} | Media Size: {row['ml']} chars")

    conn.close()

if __name__ == "__main__":
    verify()
