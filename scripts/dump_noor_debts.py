import sys
import os
import io

# Add current directory to path so imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

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
    
    if not noor_sheet:
        print("Noor sheet not found")
        exit()

    print(f"Found sheet: {noor_sheet}")
    
    total_debt = 0.0
    count = 0
    
    print("\n--- FIRST 70 LINES AUDIT (Column E) ---")
    for i in range(2, 71): # Rows 2 to 70 (User specified)
        row_vals = d.get_row_values(xml_data, noor_sheet, i)
        if not row_vals:
            continue
            
        amount = 0.0
        try:
            val_str = row_vals.get('E', '0').replace(',', '')
            if val_str:
                amount = float(val_str)
        except:
            amount = 0.0
            
        campaign = row_vals.get('A', 'Unknown')
        
        if amount >= 0: # Include 0s? or just >0? User said "Before verify everything for amount > 0". No, "All 70 first line are sure debts". I will list them all.
            total_debt += amount
            count += 1
            print(f"Row {i}: {campaign} - {amount}")
    
    print(f"\nTotal Rows Counted: {count}")
    print(f"Total Debt (First 70 lines): {total_debt:.2f}")
