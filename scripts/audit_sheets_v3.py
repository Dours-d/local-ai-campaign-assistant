import re
import os

def extract_cell(table_xml, col_name, row_idx):
    # col_name: 'AB' (28)
    col_idx = 0
    for char in col_name.upper():
        col_idx = col_idx * 26 + (ord(char) - ord('A') + 1)
    col_idx -= 1

    row_pattern = re.compile(r'<table:table-row.*?>(.*?)</table:table-row>', re.DOTALL)
    rows = row_pattern.finditer(table_xml)
    
    current_row = 0
    for match in rows:
        row_content = match.group(1)
        row_tag = match.group(0)[:match.group(0).find('>')+1]
        
        repeat_match = re.search(r'table:number-rows-repeated="(\d+)"', row_tag)
        repeat_count = int(repeat_match.group(1)) if repeat_match else 1
        
        if current_row <= row_idx < current_row + repeat_count:
            # This is the row
            cell_pattern = re.compile(r'<table:table-cell.*?>.*?</table:table-cell>|<table:covered-table-cell.*?>.*?</table:covered-table-cell>', re.DOTALL)
            cells = cell_pattern.findall(row_content)
            
            curr_col = 0
            for cell_xml in cells:
                col_repeat_match = re.search(r'table:number-columns-repeated="(\d+)"', cell_xml)
                col_repeat = int(col_repeat_match.group(1)) if col_repeat_match else 1
                
                if curr_col <= col_idx < curr_col + col_repeat:
                    return cell_xml
                
                curr_col += col_repeat
        current_row += repeat_count
    return None

def get_ann_text(xml_block):
    if not xml_block: return ""
    ann_match = re.search(r'<office:annotation.*?>.*?</office:annotation>', xml_block, re.DOTALL)
    if ann_match:
        p_texts = re.findall(r'<text:p>(.*?)</text:p>', ann_match.group(0))
        return " | ".join(p_texts)
    return ""

def get_cell_value(cell_xml):
    if not cell_xml: return None
    val_match = re.search(r'office:value="(.*?)"', cell_xml)
    if val_match: return val_match.group(1)
    # Check for string value
    str_val = re.findall(r'<text:p>(.*?)</text:p>', cell_xml)
    return " ".join(str_val) if str_val else None

content_path = 'temp_total2/content.xml'
with open(content_path, 'r', encoding='utf-8', errors='ignore') as f:
    data = f.read()

# 1. Audit Rania
print("\n--- Rania Audit ---")
r_match = re.search(r'table:name="Rania"', data, re.IGNORECASE)
if r_match:
    r_start = r_match.start()
    r_end = data.find('</table:table>', r_start)
    r_xml = data[r_start:r_end]
    
    cell_ab164 = extract_cell(r_xml, 'AB', 163)
    print(f"AB164 Value: {get_cell_value(cell_ab164)}")
    print(f"AB164 Comment: {get_ann_text(cell_ab164)}")
else:
    print("Rania sheet not found.")

# 2. Audit Ibtisam
print("\n--- Ibtisam Audit ---")
i_match = re.search(r'table:name="Ibtisam"', data, re.IGNORECASE)
if i_match:
    i_start = i_match.start()
    i_end = data.find('</table:table>', i_start)
    i_xml = data[i_start:i_end]
    
    cell_ab410 = extract_cell(i_xml, 'AB', 409)
    print(f"AB410 Value: {get_cell_value(cell_ab410)}")
    print(f"AB410 Comment: {get_ann_text(cell_ab410)}")
else:
    print("Ibtisam sheet not found.")

# 3. Global Search for interesting values
print("\n--- Global Search for Rania & Ibtisam comments ---")
for m in re.finditer(r'<office:annotation.*?</office:annotation>', data, re.DOTALL):
    ann = m.group(0)
    ann_text = get_ann_text(ann)
    if any(x in ann_text.lower() for x in ['rania', 'ibtisam', 'debt', 'comment']):
        # Find sheet
        tbl_match = re.findall(r'table:name="(.*?)"', data[:m.start()])
        sheet = tbl_match[-1] if tbl_match else "Unknown"
        print(f"Sheet: {sheet} | Comment: {ann_text}")
