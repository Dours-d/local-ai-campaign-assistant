import json
import glob
import os

def check_files():
    files = glob.glob('data/onboarding_submissions/*.json')
    for f in files:
        if os.path.getsize(f) == 0:
            print(f"EMPTY: {f}")
            continue
        try:
            with open(f, 'r', encoding='utf-8') as fh:
                json.load(fh)
        except Exception as e:
            print(f"CORRUPT: {f} - {e}")

if __name__ == "__main__":
    check_files()
