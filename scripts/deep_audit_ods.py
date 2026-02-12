import re
import os

def get_xml_block(data, start_pattern, end_pattern, start_from=0):
    match = re.search(start_pattern, data[start_from:], re.IGNORECASE)
    if not match: return None, -1, -1
    start_pos = start_from + match.start()
    end_pos = data.find(end_pattern, start_pos)
    if end_pos == -1: return data[start_pos:], start_pos, len(data)
    return data[start_pos:end_pos + len(end_pattern)], start_pos, end_pos + len(end_pattern)

def parse_ods_rows(table_xml):
    row_pattern = re.compile(r'<table:table-row.*?</table:table-row>', re.DOTALL)
    rows_raw = row_pattern.findall(table_xml)
    rows_expanded = []
    
    for row_xml in rows_raw:
        repeat_match = re.search(r'table:number-rows-repeated="(\d+)"', row_xml)
        repeat_count = int(repeat_match.group(1)) if repeat_match else 1
        
        # We don't want to expand thousands of empty rows, but we need up to 500 for Rania/Ibtisam
        if len(rows_expanded) < 1000:
            for _ in range(min(repeat_count, 1000 - len(rows_expanded))):
                rows_expanded.append(row_xml)
        else:
            break
    return rows_expanded

def extract_cell_info(row_xml, col_idx):
    # col_idx is 0-based. AB = 27
    cell_pattern = re.compile(r'<table:table-cell.*?>.*?</table:table-cell>', re.DOTALL)
    cells_raw = cell_pattern.findall(row_xml)
    
    curr_col = 0
    for cell_xml in cells_raw:
        col_repeat_match = re.search(r'table:number-columns-repeated="(\d+)"', cell_xml)
        col_repeat = int(col_repeat_match.group(1)) if col_repeat_match else 1
        
        if curr_col <= col_idx < curr_col + col_repeat:
            # Found the cell
            val_match = re.search(r'office:value="(.*?)"', cell_xml)
            value = val_match.group(1) if val_match else None
            
            p_text = " ".join(re.findall(r'<text:p>(.*?)</text:p>', cell_xml))
            
            ann_text = " "
            ann_match = re.search(r'<office:annotation.*?>.*?</office:annotation>', cell_xml, re.DOTALL)
            if ann_match:
                ann_text = " | ".join(re.findall(r'<text:p>(.*?)</text:p>', ann_match.group(0)))
            
            return {
                'xml': cell_xml,
                'value': value,
                'text': p_text,
                'comment': ann_text
            }
        curr_col += col_repeat
    return None

content_path = 'temp_total2/content.xml'
with open(content_path, 'r', encoding='utf-8', errors='ignore') as f:
    full_data = f.read()

# Audit Sheets
for sheet_name, cell_ref, row_num in [('Rania', 'AB164', 164), ('Ibtisam', 'AB410', 410)]:
    print(f"\n--- AUDITING SHEET: {sheet_name} ({cell_ref}) ---")
    table_xml, start, end = get_xml_block(full_data, f'table:name="{sheet_name}"', '</table:table>')
    
    if not table_xml:
        print(f"Sheet '{sheet_name}' not found.")
        continue
    
    print(f"Sheet discovered. Parsing rows...")
    rows = parse_ods_rows(table_xml)
    
    if len(rows) < row_num:
        print(f"Table only has {len(rows)} rows. Looking for Row {row_num} failed.")
        continue
    
    row_xml = rows[row_num - 1]
    # AB is column 28 -> index 27
    info = extract_cell_info(row_xml, 27)
    
    if info:
        print(f"Value: {info['value']}")
        print(f"Text in cell: {info['text']}")
        print(f"Comment (Annotation): {info['comment']}")
        if info['comment'] == " ":
            print("Searching nearby cells for annotations just in case...")
            # Look at entire row for any annotation
            anns = re.findall(r'<office:annotation.*?</office:annotation>', row_xml, re.DOTALL)
            if anns:
                print(f"Found {len(anns)} annotations in this row.")
                for i, ann in enumerate(anns):
                    print(f"Row Annotation {i+1}: {' | '.join(re.findall(r'<text:p>(.*?)</text:p>', ann))}")
    else:
        print("Cell info not extracted.")

    # Search globally for the name in this table just to be sure
    print(f"\nSearching for ID 138558 or 138822 in {sheet_name} table...")
    for id_val in ['138558', '138822', '150134', '5536', '11903']:
        if id_val in table_xml:
            idx = table_xml.find(id_val)
            print(f"Found '{id_val}' in {sheet_name} table at offset {idx}")
            print(f"Context: {table_xml[max(0, idx-100):idx+200]}")
