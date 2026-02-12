import re
import os

def col_to_idx(col):
    idx = 0
    for char in col:
        idx = idx * 26 + (ord(char.upper()) - ord('A') + 1)
    return idx - 1

IDX_CM = col_to_idx("CM")
IDX_CP = col_to_idx("CP")

if __name__ == "__main__":
    content_path = 'temp_total2/content.xml'
    if not os.path.exists(content_path):
        print(f"File not found: {content_path}")
        exit()

    with open(content_path, 'r', encoding='utf-8', errors='ignore') as f:
        data = f.read()

    start = data.find('table:name="Main"')
    if start == -1:
        print("Main sheet not found")
        exit()
        
    end = data.find('</table:table>', start)
    table_xml = data[start:end]

    rows = list(re.finditer(r'<table:table-row.*?>(.*?)</table:table-row>', table_xml, re.DOTALL))
    print(f"Total rows in Main: {len(rows)}")
    
    total_eur = 0.0
    count = 0
    
    for i, r in enumerate(rows):
        row_content = r.group(1)
        # Simple text check
        if 'Help Mahmod' in row_content:
            cell_pattern = re.compile(r'<(table:table-cell|table:covered-table-cell).*?(/|>(.*?)</\1)>', re.DOTALL)
            cell_matches = cell_pattern.finditer(row_content)
            
            curr_col = 0
            val_cm = 0.0
            val_cp = 0.0
            
            for cm in cell_matches:
                cell_xml = cm.group(0)
                rep_match = re.search(r'table:number-columns-repeated="(\d+)"', cell_xml)
                rep_count = int(rep_match.group(1)) if rep_match else 1
                
                val = 0.0
                v_match = re.search(r'office:value="([\d.]+)"', cell_xml)
                if v_match: val = float(v_match.group(1))
                
                # Check coverage of this cell for CM and CP
                # range [curr_col, curr_col + rep_count)
                if i+1 == 85 and curr_col > 80:
                    print(f"Row 85 Col {curr_col} val={val} rep={rep_count}")

                if curr_col <= IDX_CM < curr_col + rep_count:
                    val_cm = val
                if curr_col <= IDX_CP < curr_col + rep_count:
                    val_cp = val
                
                curr_col += rep_count
            
            if val_cp == 0:
                count += 1
                total_eur += val_cm
                if count == 1:
                    print(f"DEBUG Row {i+1}: CM={val_cm}, CP={val_cp}")

    print(f"Count: {count}")
    print(f"Total CM (EUR): {total_eur:.2f}")
