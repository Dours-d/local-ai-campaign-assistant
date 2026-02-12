
import os
import re

DATA_DIR = "data"
EXPORTS_DIR = os.path.join(DATA_DIR, "exports")
TARGETS = ["4306175", "7357942", "2238618"]

def search():
    found_any = False
    for root, dirs, files in os.walk(DATA_DIR):
        for f in files:
            full_path = os.path.join(root, f)
            # Check filename
            for t in TARGETS:
                if t in f:
                    print(f"FOUND in filename: {full_path}")
                    found_any = True
            
            # Check content (if text-like)
            if f.endswith(('.txt', '.json', '.html', '.csv')):
                try:
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as content_file:
                        content = content_file.read()
                        for t in TARGETS:
                            if t in content:
                                print(f"FOUND in content of: {full_path}")
                                found_any = True
                except: pass
    
    if not found_any:
        print("No matches found for any target sub-sequences.")

if __name__ == "__main__":
    search()
