import re
import os
import html
import sys

def visualize_sheet(sheet_name, output_f, max_rows=2000, search_text=None):
    content_path = 'temp_total2/content.xml'
    if not os.path.exists(content_path):
        output_f.write(f"Error: {content_path} not found\n")
        return

    with open(content_path, 'r', encoding='utf-8', errors='ignore') as f:
        data = f.read()
    
    # Handle entities in sheet name (exact or slightly escaped)
    pattern = sheet_name.replace("'", "&apos;").replace("&", "&amp;")
    sheet_match = re.search(f'table:name="{re.escape(sheet_name)}"', data, re.IGNORECASE)
    if not sheet_match:
        # Fallback to escaped version
        sheet_match = re.search(f'table:name="{pattern}"', data, re.IGNORECASE)
    
    if not sheet_match:
        output_f.write(f"Sheet {sheet_name} not found\n")
        return
    
    actual_name = sheet_match.group(1) if sheet_match.groups() else sheet_name
    output_f.write(f"\n--- VISUALIZING {sheet_name} (Up to {max_rows} rows) ---\n")
    
    s_start = sheet_match.start()
    s_end = data.find('</table:table>', s_start)
    table_xml = data[s_start:s_end]
    
    row_pattern = re.compile(r'<table:table-row.*?>(.*?)</table:table-row>', re.DOTALL)
    rows = row_pattern.finditer(table_xml)
    
    current_row = 1
    for match in rows:
        row_content = match.group(1)
        row_tag = match.group(0)[:match.group(0).find('>')+1]
        
        repeat_match = re.search(r'table:number-rows-repeated="(\d+)"', row_tag)
        repeat_count = int(repeat_match.group(1)) if repeat_match else 1
        
        if current_row > max_rows: break
        
        # Optimization: only process if it has content
        if '<table:table-cell' in row_content:
            cell_pattern = re.compile(r'<table:table-cell.*?>.*?</table:table-cell>|<table:covered-table-cell.*?>.*?</table:covered-table-cell>|<table:table-cell.*?/>', re.DOTALL)
            cells = cell_pattern.findall(row_content)
            
            row_data = []
            curr_col = 1
            row_text_content = ""
            for cell_xml in cells:
                col_repeat_match = re.search(r'table:number-columns-repeated="(\d+)"', cell_xml)
                col_repeat = int(col_repeat_match.group(1)) if col_repeat_match else 1
                
                val = ""
                v_match = re.search(r'office:value="(.*?)"', cell_xml)
                if v_match: val = v_match.group(1)
                else:
                    p_match = re.search(r'<text:p>(.*?)</text:p>', cell_xml)
                    if p_match: val = p_match.group(1)
                
                ann = ""
                if '<office:annotation' in cell_xml:
                    ann_xml_match = re.search(r'<office:annotation.*?</office:annotation>', cell_xml, re.DOTALL)
                    if ann_xml_match:
                         ann = " [COMMENT: " + " | ".join(re.findall(r'<text:p>(.*?)</text:p>', ann_xml_match.group(0))) + "]"
                
                if val or ann:
                    col_str = ""
                    temp_col = curr_col
                    while temp_col > 0:
                        temp_col, rem = divmod(temp_col - 1, 26)
                        col_str = chr(65 + rem) + col_str
                        
                    # Handle multi-char columns like AA, AB...
                    row_data.append(f"{col_str}: {val}{ann}")
                    row_text_content += f" {val} {ann}"
                
                curr_col += col_repeat
            
            if row_data:
                if search_text:
                    if search_text.lower() in row_text_content.lower():
                        output_f.write(f"Row {current_row}: {' | '.join(row_data)}\n")
                else:
                    output_f.write(f"Row {current_row}: {' | '.join(row_data)}\n")
        
        current_row += repeat_count

output_path = 'sheet_viz_final_audit.txt'
with open(output_path, 'w', encoding='utf-8') as out:
    targets = [
        ('Rania', 300, None),
        ('Ibtisam', 600, None),
        ('Fayez', 1000, None),
        ('Let\'s draw a smile (Ahmed\'s daughter)', 100, None),
        ('Mahmoud Basem', 1000, None),
        ('Mohammed  Suhail', 600, None),
        ('Samirah', 500, None),
        ('Main', 8000, "Mahmoud Basem"), # Extensive search in Main
        ('Main', 8000, "rebuild his life"),
        ('Main', 8000, "5536.12"),
    ]
    for name, limit, search in targets:
        visualize_sheet(name, out, limit, search)
