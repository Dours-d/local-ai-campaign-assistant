import os
import json

def main():
    phones = ["0595843932", "0597172654", "972592475288", "00972597341113"]
    # Also search for suffixes to be safe
    sub_phones = [p[-9:] for p in phones]
    
    print(f"Searching for phones: {phones} and suffixes: {sub_phones}...")
    
    data_dir = "data"
    results = []
    
    for f in os.listdir(data_dir):
        if f.endswith(".json"):
            path = os.path.join(data_dir, f)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as jf:
                    # Read as text for fast search
                    content = jf.read()
                    matches = []
                    for p in phones + sub_phones:
                        if p in content:
                            matches.append(p)
                    
                    if matches:
                        print(f"MATCH in {f}: {set(matches)}")
                        # Load and find the actual objects
                        jf.seek(0)
                        data = json.load(jf)
                        # We'll just print 1000 chars around the first match as a quick check
                        # Or search specifically for keys
                        results.append({"file": f, "matches": list(set(matches))})
            except Exception as e:
                print(f"Error reading {f}: {e}")

if __name__ == "__main__":
    main()
