
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

    # Split by the message header
    blocks = re.split(r"--- MESSAGE FOR (.*?) ---\n", content)
    
    # re.split with a capture group returns [pre-match, group, post-match, group, post-match, ...]
    # So we want to skip the first element (which is empty or contains header-less text)
    # Then iterate in pairs of ID and Body
    
    if len(blocks) < 3:
        print("No messages found in the source file.")
        return

    messages_to_write = []
    for i in range(1, len(blocks), 2):
        search_id = blocks[i].strip()
        body = blocks[i+1]
        
        # The body might contain the trailing dashes from the previous pattern
        # We clean it up by taking content until the last delimiter if present, 
        # but since we split by headers, the body is just the text until the next header.
        # We should just strip the trailing ----------------------------
        body = re.sub(r"\n-{20,}\s*$", "", body, flags=re.MULTILINE)
        
        messages_to_write.append((search_id, body.strip()))

    print(f"Splitting {len(messages_to_write)} messages...")
    
    for search_id, message_body in messages_to_write:
        # Clean the ID for filename
        filename = f"{search_id.strip()}.txt"
        file_path = os.path.join(OUTPUT_DIR, filename)
        
        with open(file_path, 'w', encoding='utf-8') as out_f:
            out_f.write(message_body.strip())
    
    print(f"Successfully created {len(messages_to_write)} individual files in {OUTPUT_DIR}")

if __name__ == "__main__":
    split_messages()
