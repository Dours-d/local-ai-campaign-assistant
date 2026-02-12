import re
import os

def idx_to_col(idx):
    col = ""
    while idx >= 0:
        idx, rem = divmod(idx, 26)
        col = chr(65 + rem) + col
        idx -= 1
    return col

def extract_row(data, sheet_name, row_idx):
    # Find exact internal name
    table_names = re.findall(r'table:name="([^"]*)"', data)
    match = None
    for name in table_names:
        clean_name = name.replace("&apos;", "'").replace("&quot;", '"')
        if sheet_name.lower() in clean_name.lower():
            match = name
            break
    
    if not match:
        print(f"Sheet '{sheet_name}' not found")
        return

    start = data.find(f'table:name="{match}"')
    end = data.find('</table:table>', start)
    table_xml = data[start:end]
    
    rows = list(re.finditer(r'<table:table-row.*?>(.*?)</table:table-row>', table_xml, re.DOTALL))
    if len(rows) < row_idx:
        print(f"Row {row_idx} not found (Total rows: {len(rows)})")
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
        
        if val.strip():
            for i in range(rep_count):
                results.append(f"{idx_to_col(curr_col + i)}: {val}")
        
        curr_col += rep_count
    
    print(f"SHEET: {match} | ROW {row_idx}")
    print(" | ".join(results))

if __name__ == "__main__":
    content_path = 'temp_total2/content.xml'
    with open(content_path, 'r', encoding='utf-8', errors='ignore') as f:
        data = f.read()
    
    extract_row(data, "smile", 21)
    extract_row(data, "Main", 1)
    extract_row(data, "Main", 10)
    extract_row(data, "Rania", 164)
    extract_row(data, "Mohammed  Suhail", 111)
