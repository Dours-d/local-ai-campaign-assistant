import sys
import os
import io

# Add current directory to path so we can import from the same folder
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

import final_dump_fixed as d
import re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

if __name__ == "__main__":
    with open('temp_total2/content.xml', 'r', encoding='utf-8', errors='ignore') as f:
        xml_data = f.read()

    # Find first sheet name
    sheet_names = re.findall(r'table:name="([^"]*)"', xml_data)
    if not sheet_names:
        print("No sheets found")
        exit()
        
    first_sheet = sheet_names[0]
    print(f"First Sheet: {first_sheet}")
    
    print("\n--- Rows 3 and 4 (First Sheet) ---")
    for i in range(3, 5):
        row_vals = d.get_row_values(xml_data, first_sheet, i)
        if row_vals:
            print(f"Row {i}: {row_vals}")
        else:
            print(f"Row {i}: Empty/Not found")

    # Also check Main if first sheet is not Main
    if first_sheet != 'Main':
        print(f"\n--- Checking 'Main' Sheet Rows 3 and 4 ---")
        for i in range(3, 5):
            row_vals = d.get_row_values(xml_data, 'Main', i)
            if row_vals:
                 print(f"Main Row {i}: {row_vals}")
