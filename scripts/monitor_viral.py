
import os
import json
from datetime import datetime

DATA_DIR = "data/onboarding_submissions"

def monitor_viral_submissions():
    if not os.path.exists(DATA_DIR):
        print(f"Error: {DATA_DIR} does not exist.")
        return

    submissions = []
    for filename in os.listdir(DATA_DIR):
        if filename.startswith("viral_") and filename.endswith("_submission.json"):
            path = os.path.join(DATA_DIR, filename)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Use file mtime as a proxy for submission date if not present
                    mtime = os.path.getmtime(path)
                    data["_submitted_at"] = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
                    submissions.append(data)
            except Exception as e:
                print(f"Error reading {filename}: {e}")

    if not submissions:
        print("No viral submissions found.")
        return

    # Sort by submission date (newest first)
    submissions.sort(key=lambda x: x.get("_submitted_at", ""), reverse=True)

    print(f"\n{'='*80}")
    print(f"{'VIRAL ONBOARDING MONITOR':^80}")
    print(f"{'='*80}\n")

    print(f"{'Date':<20} | {'WhatsApp':<15} | {'Display Name':<20} | {'Flagged':<7}")
    print("-" * 80)

    for s in submissions:
        date = s.get("_submitted_at", "N/A")
        wa = s.get("whatsapp_number", "N/A")
        name = s.get("display_name", "N/A")[:20]
        flagged = "YES [!]" if s.get("flagged_for_review", False) else "NO"
        
        print(f"{date:<20} | {wa:<15} | {name:<20} | {flagged:<7}")
        if s.get("title"):
            print(f"  Title: {s.get('title')}")
        if s.get("flagged_for_review") and s.get("files"):
            flagged_media = [f["path"] for f in s["files"] if f.get("is_flagged")]
            if flagged_media:
                print(f"  [!] Flagged Media: {', '.join(flagged_media)}")
        print("-" * 80)

    print(f"\nTotal Viral Submissions: {len(submissions)}")

if __name__ == "__main__":
    monitor_viral_submissions()
