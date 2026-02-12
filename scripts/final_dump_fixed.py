import re
import os

def idx_to_col(idx):
    col = ""
    while idx >= 0:
        idx, rem = divmod(idx, 26)
        col = chr(65 + rem) + col
        idx -= 1
    return col

def dump_headers(data, sheet_name):
    # Try different name variations
    names_to_try = [
        sheet_name,
        sheet_name.replace("'", "&apos;"),
    ]
    
    sheet_match = None
    for name in names_to_try:
        pattern = f'table:name="{name}"'
        sheet_match = re.search(pattern, data)
        if sheet_match: break
    
    if not sheet_match: return None

    start = sheet_match.start()
    end = data.find('</table:table>', start)
    table_xml = data[start:end]
    rows = list(re.finditer(r'<table:table-row.*?>(.*?)</table:table-row>', table_xml, re.DOTALL))
    if len(rows) > 0:
        row_content = rows[0].group(1)
        cell_pattern = re.compile(r'<(table:table-cell|table:covered-table-cell).*?(/|>(.*?)</\1)>', re.DOTALL)
        cell_matches = cell_pattern.finditer(row_content)
        row_data = {}
        curr_col = 0
        for cm in cell_matches:
            cell_xml = cm.group(0)
            rep_match = re.search(r'table:number-columns-repeated="(\d+)"', cell_xml)
            rep_count = int(rep_match.group(1)) if rep_match else 1
            p_match = re.search(r'<text:p>(.*?)</text:p>', cell_xml)
            val = p_match.group(1) if p_match else ""
            for i in range(rep_count):
                if val: row_data[idx_to_col(curr_col + i)] = val
            curr_col += rep_count
        return row_data
    return None

def get_row_values(data, sheet_name, row_idx):
    names_to_try = [
        sheet_name,
        sheet_name.replace("'", "&apos;"),
    ]
    sheet_match = None
    for name in names_to_try:
        pattern = f'table:name="{name}"'
        sheet_match = re.search(pattern, data)
        if sheet_match: break
    if not sheet_match: return None

    start = sheet_match.start()
    end = data.find('</table:table>', start)
    table_xml = data[start:end]
    rows = list(re.finditer(r'<table:table-row.*?>(.*?)</table:table-row>', table_xml, re.DOTALL))
    
    if len(rows) < row_idx: return None

    row_content = rows[row_idx-1].group(1)
    cell_pattern = re.compile(r'<(table:table-cell|table:covered-table-cell).*?(/|>(.*?)</\1)>', re.DOTALL)
    cell_matches = cell_pattern.finditer(row_content)
    
    curr_col = 0
    results = {}
    for cm in cell_matches:
        cell_xml = cm.group(0)
        rep_match = re.search(r'table:number-columns-repeated="(\d+)"', cell_xml)
        rep_count = int(rep_match.group(1)) if rep_match else 1
        val = ""
        v_match = re.search(r'office:value="([^"]*)"', cell_xml)
        if v_match: val = v_match.group(1)
        else:
            p_match = re.search(r'<text:p>(.*?)</text:p>', cell_xml)
            if p_match: val = p_match.group(1)
        
        for i in range(rep_count):
            col_id = idx_to_col(curr_col + i)
            if val.strip():
                results[col_id] = val
            curr_col += rep_count
    return results

def dump_row(data, sheet_name, row_idx, headers):
    names_to_try = [
        sheet_name,
        sheet_name.replace("'", "&apos;"),
    ]
    sheet_match = None
    for name in names_to_try:
        pattern = f'table:name="{name}"'
        sheet_match = re.search(pattern, data)
        if sheet_match: break
    if not sheet_match: return

    start = sheet_match.start()
    end = data.find('</table:table>', start)
    table_xml = data[start:end]
    rows = list(re.finditer(r'<table:table-row.*?>(.*?)</table:table-row>', table_xml, re.DOTALL))
    
    if len(rows) < row_idx:
        print(f"Sheet {sheet_name} row {row_idx} not found")
        return

    row_content = rows[row_idx-1].group(1)
    cell_pattern = re.compile(r'<(table:table-cell|table:covered-table-cell).*?(/|>(.*?)</\1)>', re.DOTALL)
    cell_matches = cell_pattern.finditer(row_content)
    
    curr_col = 0
    results = []
    for cm in cell_matches:
        cell_xml = cm.group(0)
        rep_match = re.search(r'table:number-columns-repeated="(\d+)"', cell_xml)
        rep_count = int(rep_match.group(1)) if rep_match else 1
        val = ""
        v_match = re.search(r'office:value="([^"]*)"', cell_xml)
        if v_match: val = v_match.group(1)
        else:
            p_match = re.search(r'<text:p>(.*?)</text:p>', cell_xml)
            if p_match: val = p_match.group(1)
        
        for i in range(rep_count):
            col_id = idx_to_col(curr_col + i)
            if val.strip():
                label = headers.get(col_id, col_id)
                results.append(f"{col_id}({label}): {val}")
            curr_col += rep_count
    print(f"\n--- {sheet_name} ROW {row_idx} ---")
    for r in results:
        print(f"  {r}")

if __name__ == "__main__":
    content_path = 'temp_total2/content.xml'
    with open(content_path, 'r', encoding='utf-8', errors='ignore') as f:
        xml_data = f.read()
    
    targets = [
        ("Let's draw a smile (Ahmed's daughter)", 21),
        ("Rania", 164),
        ("Mohammed  Suhail", 111),
        ("Ibtisam", 410),
        ("Fayez", 895),
        ("Mahmoud Basem", 492),
        ("Samirah", 350)
    ]
    
    main_headers = dump_headers(xml_data, "Main")
    
    for s, r in targets:
        h = dump_headers(xml_data, s)
        if not h: h = main_headers # Fallback to Main headers if sheet headers not found
        dump_row(xml_data, s, r, h)
