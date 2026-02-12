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

def get_sheet_annotations(table_xml, sheet_name):
    row_pattern = re.compile(r'<table:table-row.*?>(.*?)</table:table-row>', re.DOTALL)
    rows = row_pattern.finditer(table_xml)
    
    current_row = 1
    found = []
    
    for match in rows:
        row_content = match.group(1)
        row_tag = match.group(0)[:match.group(0).find('>')+1]
        
        repeat_match = re.search(r'table:number-rows-repeated="(\d+)"', row_tag)
        repeat_count = int(repeat_match.group(1)) if repeat_match else 1
        
        if '<office:annotation' in row_content:
            cell_pattern = re.compile(r'<table:table-cell.*?>.*?</table:table-cell>|<table:covered-table-cell.*?>.*?</table:covered-table-cell>', re.DOTALL)
            cells = cell_pattern.findall(row_content)
            
            curr_col = 1
            for cell_xml in cells:
                col_repeat_match = re.search(r'table:number-columns-repeated="(\d+)"', cell_xml)
                col_repeat = int(col_repeat_match.group(1)) if col_repeat_match else 1
                
                if '<office:annotation' in cell_xml:
                    ann_match = re.search(r'<office:annotation.*?>.*?</office:annotation>', cell_xml, re.DOTALL)
                    ann_xml = ann_match.group(0)
                    p_texts = re.findall(r'<text:p>(.*?)</text:p>', ann_xml)
                    
                    col_str = ""
                    temp_col = curr_col
                    while temp_col > 0:
                        temp_col, rem = divmod(temp_col - 1, 26)
                        col_str = chr(65 + rem) + col_str
                    
                    val = re.search(r'office:value="(.*?)"', cell_xml).group(1) if 'office:value="' in cell_xml else "N/A"
                    if val == "N/A":
                        tp = re.findall(r'<text:p>(.*?)</text:p>', cell_xml)
                        val = " ".join(tp) if tp else "EMPTY"

                    found.append({
                        'sheet': sheet_name,
                        'cell': f"{col_str}{current_row}",
                        'text': " | ".join(p_texts),
                        'value': val
                    })
                
                curr_col += col_repeat
        
        current_row += repeat_count
    return found

content_path = 'temp_total2/content.xml'
with open(content_path, 'r', encoding='utf-8', errors='ignore') as f:
    data = f.read()

all_found = []
for sheet in ['Rania', 'Ibtisam', 'Fayez']:
    match = re.search(f'table:name="{sheet}"', data, re.IGNORECASE)
    if match:
        s_start = match.start()
        s_end = data.find('</table:table>', s_start)
        table_xml = data[s_start:s_end]
        all_found.extend(get_sheet_annotations(table_xml, sheet))

print("--- ANNOTATIONS FOUND ---")
for item in all_found:
    print(f"[{item['sheet']} {item['cell']}] Value: {item['value']} | Comment: {item['text']}")

# Target specific cells
print("\n--- TARGET CELL AUDIT ---")
for sheet, cell, row_idx in [('Rania', 'AB164', 164), ('Ibtisam', 'AB410', 410), ('Fayez', 'AB895', 895)]:
    match = re.search(f'table:name="{sheet}"', data, re.IGNORECASE)
    if match:
        s_start = match.start()
        s_end = data.find('</table:table>', s_start)
        table_xml = data[s_start:s_end]
        cell_xml = extract_cell(table_xml, 'AB', row_idx-1)
        if cell_xml:
            val = re.search(r'office:value="(.*?)"', cell_xml).group(1) if 'office:value="' in cell_xml else "N/A"
            if val == "N/A":
                tp = re.findall(r'<text:p>(.*?)</text:p>', cell_xml)
                val = " ".join(tp) if tp else "EMPTY"
            
            ann = get_ann_text(cell_xml)
            print(f"Sheet: {sheet} | Cell: {cell} | Value: {val} | Comment: {ann}")
        else:
            print(f"Sheet: {sheet} | Cell: {cell} | Status: NOT FOUND (Check repeated rows logic)")
    else:
        print(f"Sheet: {sheet} | Status: NOT FOUND")
