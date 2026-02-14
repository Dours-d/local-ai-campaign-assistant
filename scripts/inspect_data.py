import os
import re

def main():
    print("--- MESSAGE SAMPLES ---")
    messages_dir = "data/trustee_messages"
    if os.path.exists(messages_dir):
        for f in os.listdir(messages_dir):
            if f.endswith(".txt"):
                path = os.path.join(messages_dir, f)
                try:
                    with open(path, 'r', encoding='utf-8') as mf:
                        content = mf.read()
                    print(f"FILE: {f}\n{content[:200]}\n---")
                    
                    # Search for chuffed links
                    if "chuffed.org" in content:
                        print(f"LINK FOUND in {f}: {re.findall(r'https?://chuffed\.org/project/\d+', content)}")
                except Exception as e:
                     print(f"Error reading {f}: {e}")
    
    print("\n--- LOG SUCCESS CONTEXT ---")
    log_path = "data/batch_run_new_trustees_v18.log"
    if os.path.exists(log_path):
        try:
            with open(log_path, 'r', encoding='utf-8', errors='ignore') as log_file:
                log_content = log_file.read()
            
            for m in list(re.finditer('SUCCESS', log_content))[:10]:
                start = max(0, m.start() - 500)
                end = min(len(log_content), m.end() + 500)
                print(f"CONTEXT around SUCCESS at {m.start()}:\n{log_content[start:end]}\n---")
        except Exception as e:
             print(f"Error reading log: {e}")

if __name__ == "__main__":
    main()
