import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

import scripts.final_dump_fixed as d
import re

if __name__ == "__main__":
    with open('temp_total2/content.xml', 'r', encoding='utf-8', errors='ignore') as f:
        xml_data = f.read()

    # Find sheet name matching "Noor"
    sheet_names = re.findall(r'table:name="([^"]*)"', xml_data)
    noor_sheet = None
    for name in sheet_names:
        if 'noor' in name.lower():
            noor_sheet = name
            break
            
    if not noor_sheet: exit()

    cols_to_check = ['E', 'F', 'G', 'AI', 'AB', 'AC']
    
    print(f"Sheet: {noor_sheet}")
    for i in range(2, 6):
        print(f"\n--- Row {i} ---")
        row_vals = d.get_row_values(xml_data, noor_sheet, i)
        if row_vals:
            for c in cols_to_check:
                print(f"{c}: {row_vals.get(c, 'EMPTY')}")
