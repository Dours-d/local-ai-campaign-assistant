import sys
import os

# Add current directory to path so imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

import scripts.final_dump_fixed as d
import re

if __name__ == "__main__":
    with open('temp_total2/content.xml', 'r', encoding='utf-8', errors='ignore') as f:
        xml_data = f.read()

    # Find rows with Mahmod
    start = xml_data.find('table:name="Main"')
    end = xml_data.find('</table:table>', start)
    table_xml = xml_data[start:end]
    rows = list(re.finditer(r'<table:table-row.*?>(.*?)</table:table-row>', table_xml, re.DOTALL))
    
    total_eur = 0.0
    count = 0
    
    print("Scanning for Mahmod...")
    for i, r in enumerate(rows):
        if 'Help Mahmod' in r.group(1):
            # i is 0-indexed, so row_idx is i+1
            vals = d.get_row_values(xml_data, 'Main', i+1)
            if vals:
                try:
                    cm_val = float(vals.get('CM', 0))
                    cp_val = float(vals.get('CP', 0))
                    if cp_val == 0:
                        total_eur += cm_val
                        count += 1
                        if count <= 5:
                            print(f"Row {i+1}: CM={cm_val}")
                except Exception as e:
                    print(f"Row {i+1} parse error: {e}")

    print(f"Total Count: {count}")
    print(f"Total Sum (CM): {total_eur:.2f}")
