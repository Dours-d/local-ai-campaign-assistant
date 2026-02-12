import re
import os

def extract_precise_cell(sheet_name, row_idx, col_name):
    # col_name like 'AB'
    content_path = 'temp_total2/content.xml'
    with open(content_path, 'r', encoding='utf-8', errors='ignore') as f:
        data = f.read()
    
    sheet_match = re.search(f'table:name=\"{re.escape(sheet_name)}\"', data)
    if not sheet_match:
        # Try escaped
        escaped_name = sheet_name.replace("'", "&apos;")
        sheet_match = re.search(f'table:name=\"{re.escape(escaped_name)}\"', data)
    
    if not sheet_match:
        return f"Sheet '{sheet_name}' not found"

    start = sheet_match.start()
    end = data.find('</table:table>', start)
    table_xml = data[start:end]
    
    rows = list(re.finditer(r'<table:table-row.*?>(.*?)</table:table-row>', table_xml, re.DOTALL))
    
    if row_idx > len(rows):
        return f"Row {row_idx} not found (Total rows: {len(rows)})"
    
    row_xml = rows[row_idx-1].group(0)
    
    # Calculate column index
    def col_to_idx(col):
        idx = 0
        for char in col:
            idx = idx * 26 + (ord(char.upper()) - ord('A') + 1)
        return idx - 1

    target_idx = col_to_idx(col_name)
    
    cell_pattern = re.compile(r'<(table:table-cell|table:covered-table-cell).*?(/|>(.*?)</\1)>', re.DOTALL)
    cell_matches = cell_pattern.finditer(rows[row_idx-1].group(1))
    
    curr_idx = 0
    for cm in cell_matches:
        cell_xml = cm.group(0)
        rep_match = re.search(r'table:number-columns-repeated="(\d+)"', cell_xml)
        rep_count = int(rep_match.group(1)) if rep_match else 1
        
        if curr_idx <= target_idx < (curr_idx + rep_count):
            # Found it
            val = ""
            v_match = re.search(r'office:value="([\d.]+)"', cell_xml)
            if v_match: val = v_match.group(1)
            else:
                p_match = re.search(r'<text:p>(.*?)</text:p>', cell_xml)
                if p_match: val = p_match.group(1)
            
            ann = ""
            if '<office:annotation' in cell_xml:
                ann_xml = re.search(r'<office:annotation.*?</office:annotation>', cell_xml, re.DOTALL).group(0)
                ann = " | ".join(re.findall(r'<text:p>(.*?)</text:p>', ann_xml))
            
            return {'value': val, 'comment': ann, 'xml': cell_xml}
        
        curr_idx += rep_count
        
    return "Column not found"

if __name__ == "__main__":
    # Ahmed: Let's draw a smile (Ahmed's daughter) ? AB21
    # Actually, let's try the name exactly as it appears in the XML
    res = extract_precise_cell("Let's draw a smile (Ahmed's daughter)", 21, "AB")
    print(f"Ahmed (AB21): {res}")
    
    res_rania = extract_precise_cell("Rania", 164, "AB")
    print(f"Rania (AB164): {res_rania}")
