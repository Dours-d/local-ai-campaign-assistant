import re
import os

def extract_cell(table_xml, col_name, row_idx):
    # row_idx is 0-based
    # col_name: 'AB' (28)
    col_idx = 0
    for char in col_name.upper():
        col_idx = col_idx * 26 + (ord(char) - ord('A') + 1)
    col_idx -= 1

    row_pattern = re.compile(r'<table:table-row.*?</table:table-row>', re.DOTALL)
    rows = row_pattern.findall(table_xml)
    
    current_row = 0
    for i, row_xml in enumerate(rows):
        repeat_match = re.search(r'table:number-rows-repeated="(\d+)"', row_xml)
        repeat_count = int(repeat_match.group(1)) if repeat_match else 1
        
        if current_row <= row_idx < current_row + repeat_count:
            cell_pattern = re.compile(r'<table:table-cell.*?>.*?</table:table-cell>', re.DOTALL)
            cells = cell_pattern.findall(row_xml)
            
            curr_col = 0
            for cell_xml in cells:
                col_repeat_match = re.search(r'table:number-columns-repeated="(\d+)"', cell_xml)
                col_repeat = int(col_repeat_match.group(1)) if col_repeat_match else 1
                
                if curr_col <= col_idx < curr_col + col_repeat:
                    return cell_xml
                
                curr_col += col_repeat
        current_row += repeat_count
    return None

def get_ann_text(cell_xml):
    if not cell_xml: return "Cell not found"
    ann_match = re.search(r'<office:annotation.*?>.*?</office:annotation>', cell_xml, re.DOTALL)
    if ann_match:
        p_texts = re.findall(r'<text:p>(.*?)</text:p>', ann_match.group(0))
        return " | ".join(p_texts)
    return "No annotation"

content_path = 'temp_total2/content.xml'
if not os.path.exists(content_path):
    print("Content XML not found")
    exit(1)

with open(content_path, 'r', encoding='utf-8', errors='ignore') as f:
    data = f.read()

def audit_sheet(sheet_name, cell_ref, row_idx):
    col_name = re.match(r'([A-Z]+)', cell_ref).group(1)
    print(f"\n--- AUDIT: {sheet_name} ({cell_ref}) ---")
    # Search for table with name containing sheet_name (case-insensitive)
    match = re.search(f'table:name="[^"]*{sheet_name}[^"]*"', data, re.IGNORECASE)
    if not match:
        print(f"Sheet matching '{sheet_name}' not found.")
        return
    
    actual_name = re.search(r'table:name="(.*?)"', match.group(0)).group(1)
    print(f"Found Sheet: {actual_name}")
    
    start_pos = match.start()
    end_pos = data.find('</table:table>', start_pos)
    table_xml = data[start_pos:end_pos]
    
    # 1. Look for specific cell
    cell_xml = extract_cell(table_xml, col_name, row_idx - 1)
    if cell_xml:
        print(f"Target Cell {cell_ref} XML: {cell_xml}")
        print(f"Target Cell Comment: {get_ann_text(cell_xml)}")
        val_match = re.search(r'office:value="(.*?)"', cell_xml)
        if val_match:
            print(f"Target Cell Value: {val_match.group(1)}")
    
    # 2. Look for ANY annotations in this sheet
    print(f"Searching for all annotations in sheet '{actual_name}'...")
    for m in re.finditer(r'<office:annotation.*?</office:annotation>', table_xml, re.DOTALL):
        ann = m.group(0)
        # Find cell context (walk back a bit)
        context = table_xml[max(0, m.start()-200):m.start()]
        print(f"Found Annotation at offset {m.start()}:")
        print(f"Context: {context}")
        print(f"Text: {get_ann_text(ann)}")
        print("-" * 30)

audit_sheet('Rania', 'AB164', 164)
# Try a few variations for Ibtisam
audit_sheet('Ibtisam', 'AB410', 410)
