import re
import os
import html

def extract_cell(table_xml, col_name, row_idx):
    # col_name: 'AB' (28)
    col_idx = 0
    for char in col_name.upper():
        col_idx = col_idx * 26 + (ord(char) - ord('A') + 1)
    col_idx -= 1

    row_pattern = re.compile(r'<table:table-row.*?>(.*?)</table:table-row>', re.DOTALL)
    row_tag_pattern = re.compile(r'<table:table-row(.*?)/?>', re.DOTALL)
    
    rows = row_pattern.finditer(table_xml)
    
    current_row = 0
    for match in rows:
        row_content = match.group(1)
        full_row_xml = match.group(0)
        row_tag_match = row_tag_pattern.search(full_row_xml)
        row_tag_attrs = row_tag_match.group(1) if row_tag_match else ""
        
        repeat_match = re.search(r'table:number-rows-repeated="(\d+)"', row_tag_attrs)
        repeat_count = int(repeat_match.group(1)) if repeat_match else 1
        
        if current_row <= row_idx < current_row + repeat_count:
            # Found the row or row segment
            cell_pattern = re.compile(r'<table:table-cell.*?>.*?</table:table-cell>|<table:covered-table-cell.*?>.*?</table:covered-table-cell>|<table:table-cell.*?/>', re.DOTALL)
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
    ann_match = re.search(r'<office:annotation.*?>(.*?)</office:annotation>', xml_block, re.DOTALL)
    if ann_match:
        p_texts = re.findall(r'<text:p>(.*?)</text:p>', ann_match.group(1))
        return " | ".join(p_texts)
    return ""

def get_cell_value(cell_xml):
    if not cell_xml: return "Cell not found"
    val_match = re.search(r'office:value="(.*?)"', cell_xml)
    if val_match: return val_match.group(1)
    # Check for string value in text:p
    str_val = re.findall(r'<text:p>(.*?)</text:p>', cell_xml)
    # Filter out text inside annotations
    if '<office:annotation' in cell_xml:
        cell_xml_no_ann = re.sub(r'<office:annotation.*?</office:annotation>', '', cell_xml, flags=re.DOTALL)
        str_val = re.findall(r'<text:p>(.*?)</text:p>', cell_xml_no_ann)
    
    return " ".join(str_val) if str_val else "Empty"

content_path = 'temp_total2/content.xml'
with open(content_path, 'r', encoding='utf-8', errors='ignore') as f:
    data = f.read()

# Targets from user
targets = [
    ('Rania', 'AB164', 164),
    ('Ibtisam', 'AB410', 410),
    ('Fayez', 'AB895', 895),
    ('Let\'s draw a smile', 'AB21', 21)
]

print("--- AUDIT RESULTS ---")
for sheet_base, cell_ref, row_num in targets:
    # Use fuzzy search for sheet name to handle entities like &apos;
    # Convert "Let's" to "Let.s" for regex
    pattern = sheet_base.replace("'", ".")
    sheet_match = re.search(f'table:name="([^"]*{pattern}[^"]*)"', data, re.IGNORECASE)
    
    if not sheet_match:
        print(f"\nTarget: {sheet_base} {cell_ref}")
        print("Status: Sheet NOT found")
        continue
    
    actual_name = sheet_match.group(1)
    print(f"\nTarget: {sheet_base} ({actual_name}) {cell_ref}")
    
    s_start = sheet_match.start()
    s_end = data.find('</table:table>', s_start)
    table_xml = data[s_start:s_end]
    
    cell_xml = extract_cell(table_xml, 'AB', row_num - 1)
    if cell_xml:
        val = get_cell_value(cell_xml)
        comment = get_ann_text(cell_xml)
        print(f"Value: {val}")
        print(f"Comment: {comment if comment else 'None found in cell'}")
        if not comment:
            # Check for any annotations in the entire row
            # Need to get row XML again... simpler to just search the table_xml for any annotation
            pass
    else:
        print("Status: Cell not found (check logic)")

    # Print any annotations found in this sheet for these names
    print(f"Annotations in sheet '{actual_name}' mentioning keywords:")
    for m in re.finditer(r'<office:annotation.*?</office:annotation>', table_xml, re.DOTALL):
        ann_text = get_ann_text(m.group(0))
        if any(kw.lower() in ann_text.lower() for kw in [sheet_base.split()[0], 'debt', 'comment']):
             print(f" - {ann_text}")
