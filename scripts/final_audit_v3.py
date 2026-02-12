import re
import os

def idx_to_col(idx):
    col = ""
    while idx >= 0:
        idx, rem = divmod(idx, 26)
        col = chr(65 + rem) + col
        idx -= 1
    return col

def get_row_dict(data, sheet_search, row_idx):
    table_names = re.findall(r'table:name="([^"]*)"', data)
    match = None
    for name in table_names:
        clean_name = name.replace("&apos;", "'").replace("&quot;", '"')
        if sheet_search.lower() in clean_name.lower():
            match = name
            break
    if not match: return None
    
    start = data.find(f'table:name="{match}"')
    end = data.find('</table:table>', start)
    table_xml = data[start:end]
    rows = list(re.finditer(r'<table:table-row.*?>(.*?)</table:table-row>', table_xml, re.DOTALL))
    
    if len(rows) < row_idx: return None
    
    row_content = rows[row_idx-1].group(1)
    cell_pattern = re.compile(r'<(table:table-cell|table:covered-table-cell).*?(/|>(.*?)</\1)>', re.DOTALL)
    cell_matches = cell_pattern.finditer(row_content)
    
    curr_col = 0
    row_data = {}
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
            if val.strip():
                row_data[idx_to_col(curr_col + i)] = val
        curr_col += rep_count
    return {'sheet': match, 'data': row_data}

if __name__ == "__main__":
    content_path = 'temp_total2/content.xml'
    with open(content_path, 'r', encoding='utf-8', errors='ignore') as f:
        data = f.read()
    
    targets = [
        ("smile", 21),
        ("Rania", 164),
        ("Suhail", 111),
        ("Fayez", 895),
        ("Ibtisam", 410),
        ("Basem", 492),
        ("Samirah", 350),
        ("Main", 1)
    ]
    
    print(f"{'Sheet':<40} | {'Row':<4} | Highlights")
    print("-" * 100)
    for s, r in targets:
        # Get Header
        h = get_row_dict(data, s, 1)
        # Get Row
        row = get_row_dict(data, s, r)
        
        if row:
            # Extract key columns like AB, AC, AF, AG, AA
            keys = ['A', 'AA', 'AB', 'AC', 'AD', 'AE', 'AF', 'AG']
            vals = []
            for k in keys:
                if k in row['data']:
                    label = h['data'].get(k, k) if h else k
                    vals.append(f"{k}({label}): {row['data'][k]}")
            print(f"{row['sheet'][:40]:<40} | {r:<4} | {' | '.join(vals)}")
