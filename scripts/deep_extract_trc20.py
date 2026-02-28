import os
import re
import json
from html.parser import HTMLParser

# Paths
EXPORTS_DIR = "data/exports"
OUTPUT_FILE = "data/trc20_deep_recovery.json"

# TRC20 Pattern
TRC20_PATTERN = re.compile(r'T[1-9A-HJ-NP-Za-km-z]{33}')

class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []

    def handle_data(self, data):
        self.text.append(data)

    def get_text(self):
        return " ".join(self.text)

def deep_extract():
    print("Starting Deep TRC20 Extraction from HTML exports...")
    results = {}
    
    html_files = [f for f in os.listdir(EXPORTS_DIR) if f.endswith(".html")]
    print(f"Found {len(html_files)} HTML files to scan.")

    for filename in html_files:
        filepath = os.path.join(EXPORTS_DIR, filename)
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                # Use a custom parser to get clean text (ripgrep might struggle with dense HTML)
                parser = TextExtractor()
                parser.feed(content)
                text = parser.get_text()
                
                matches = TRC20_PATTERN.findall(text)
                if matches:
                    print(f"  [+] Found {len(set(matches))} addresses in {filename}")
                    for addr in set(matches):
                        if addr not in results:
                            results[addr] = []
                        results[addr].append(filename)
        except Exception as e:
            print(f"Error processing {filename}: {e}")

    # Save results
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    print(f"\nExtraction complete. Total unique addresses found: {len(results)}")
    print(f"Results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    deep_extract()
