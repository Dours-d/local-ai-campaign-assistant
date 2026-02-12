
import os
import zipfile
import re

GGF_DIR = "GGF"
TARGET_NUMBERS = ["4306175", "7357942", "2238618", "creations", "creation"]

def search_in_ods(file_path):
    try:
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            if 'content.xml' in zip_ref.namelist():
                content = zip_ref.read('content.xml').decode('utf-8')
                for num in TARGET_NUMBERS:
                    idx = content.lower().find(num.lower())
                    if idx != -1:
                        context = content[max(0, idx-100):idx+200]
                        print(f"FOUND '{num}' in {file_path}")
                        print(f"Context: {context}\n")
    except Exception as e:
        print(f"Error reading {file_path}: {e}")

if __name__ == "__main__":
    for f in os.listdir(GGF_DIR):
        if f.endswith(".ods"):
            search_in_ods(os.path.join(GGF_DIR, f))
