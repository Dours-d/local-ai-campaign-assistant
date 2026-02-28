import os
import re
import json

# Paths
EXPORTS_DIR = "data/exports"
OUTPUT_DIAG = "data/trc20_diagnostics.txt"

# Very broad pattern for any T... address to see what we are hitting
BROAD_PATTERN = re.compile(r'T[A-Za-z0-9]{30,40}')

def diagnose():
    print("Starting TRC20 Diagnostic Discovery...")
    found_strings = {}

    for filename in os.listdir(EXPORTS_DIR):
        filepath = os.path.join(EXPORTS_DIR, filename)
        if not os.path.isfile(filepath): continue
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                # Check for "T" addresses
                matches = BROAD_PATTERN.findall(content)
                if matches:
                    print(f"DEBUG: Found matches in {filename}")
                    for m in matches:
                        found_strings[m] = found_strings.get(m, 0) + 1
        except Exception as e:
            pass

    with open(OUTPUT_DIAG, 'w', encoding='utf-8') as f:
        f.write("TRC20 Diagnostic Discovery Results\n")
        f.write("==================================\n\n")
        sorted_hits = sorted(found_strings.items(), key=lambda x: x[1], reverse=True)
        for s, count in sorted_hits:
            f.write(f"{s} (Hits: {count})\n")

    print(f"Discovery complete. Found {len(found_strings)} candidate strings.")

if __name__ == "__main__":
    diagnose()
