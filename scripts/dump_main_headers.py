import sys
import os

# Add current directory to path so imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

import scripts.final_dump_fixed as d

if __name__ == "__main__":
    with open('temp_total2/content.xml', 'r', encoding='utf-8', errors='ignore') as f:
        xml_data = f.read()

    headers = d.dump_headers(xml_data, 'Main')
    if headers:
        for col in ['CJ', 'CK', 'CL', 'CM', 'CN', 'CO', 'CP', 'CQ']:
            print(f"{col}: {headers.get(col, 'UNKNOWN')}")
    else:
        print("Main headers not found")
