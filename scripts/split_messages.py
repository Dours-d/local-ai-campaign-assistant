
import os
import re

SOURCE_FILE = "data/onboarding_messages.txt"
OUTPUT_DIR = "data/onboarding_outbox"

def split_messages():
    if not os.path.exists(SOURCE_FILE):
        print(f"Error: {SOURCE_FILE} not found.")
        return

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created directory: {OUTPUT_DIR}")

    with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # Messages are separated by delimiters and start with a header
    # --- MESSAGE FOR <ID> ---
    # ... message ...
    # ----------------------------
    
    pattern = r"--- MESSAGE FOR (.*?) ---\n(.*?)\n-{28,}"
    matches = re.findall(pattern, content, re.DOTALL)

    if not matches:
        print("No messages found in the source file.")
        return

    print(f"Splitting {len(matches)} messages...")
    
    for search_id, message_body in matches:
        # Clean the ID for filename
        filename = f"{search_id.strip()}.txt"
        file_path = os.path.join(OUTPUT_DIR, filename)
        
        with open(file_path, 'w', encoding='utf-8') as out_f:
            out_f.write(message_body.strip())
    
    print(f"Successfully created {len(matches)} individual files in {OUTPUT_DIR}")

if __name__ == "__main__":
    split_messages()
