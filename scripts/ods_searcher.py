import re
import os

def search_ods(xml_path):
    if not os.path.exists(xml_path):
        print(f"File not found: {xml_path}")
        return

    with open(xml_path, 'r', encoding='utf-8', errors='ignore') as f:
        # Read file in chunks to avoid memory issues if it was even larger, 
        # but 37MB is fine to read at once.
        content = f.read()

    print("--- SHEET NAMES ---")
    sheet_names = re.findall(r'table:name="([^"]*)"', content)
    for name in sheet_names:
        print(name)

    print("\n--- SEARCH: '5536' ---")
    for match in re.finditer(r'[^<]{0,50}5536[^>]{0,50}', content):
        print(f"Context: ...{match.group(0)}...")

    print("\n--- SEARCH: 'rebuild his life' ---")
    for match in re.finditer(r'[^<]{0,100}rebuild his life[^>]{0,100}', content):
        print(f"Context: ...{match.group(0)}...")

    print("\n--- SEARCH: 'USDT' ---")
    # Search for USDT specifically in annotations or text:p
    for match in re.finditer(r'[^<]{0,50}USDT[^>]{0,50}', content, re.IGNORECASE):
        print(f"Context: ...{match.group(0)}...")

    print("\n--- TARGET CELLS CHECK ---")
    # Try to find specific row/cell markers if possible
    # This is harder without a full parser but let's look for literals
    for target in ["AB164", "AB410", "AB895", "AB21", "AB492", "AB111", "AG350"]:
        if target in content:
            print(f"Found literal '{target}' in XML")

if __name__ == "__main__":
    search_ods('temp_total2/content.xml')
