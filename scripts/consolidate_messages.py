import os

OUTBOX_DIR = "data/onboarding_outbox"
OUTPUT_FILE = "onboarding_messages.txt"

def consolidate():
    if not os.path.exists(OUTBOX_DIR):
        print(f"Outbox {OUTBOX_DIR} not found.")
        return
    
    files = sorted([f for f in os.listdir(OUTBOX_DIR) if f.endswith("_onboarding.txt")])
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        for filename in files:
            # Extract ID from filename (e.g., 972592113473_onboarding.txt)
            bid = filename.replace("_onboarding.txt", "")
            
            with open(os.path.join(OUTBOX_DIR, filename), "r", encoding="utf-8") as f:
                content = f.read()
            
            out.write(f"--- MESSAGE FOR {bid} ---\n")
            out.write(content)
            out.write("\n" + "-"*30 + "\n\n")
            
    print(f"Consolidated {len(files)} messages into {OUTPUT_FILE}")

if __name__ == "__main__":
    consolidate()
