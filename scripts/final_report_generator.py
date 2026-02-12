import re
import os

def idx_to_col(idx):
    col = ""
    while idx >= 0:
        idx, rem = divmod(idx, 26)
        col = chr(65 + rem) + col
        idx -= 1
    return col

def get_row_data(data, sheet_search, row_idx):
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
            if val.strip(): row_data[idx_to_col(curr_col + i)] = val
        curr_col += rep_count
    return row_data

if __name__ == "__main__":
    content_path = 'temp_total2/content.xml'
    with open(content_path, 'r', encoding='utf-8', errors='ignore') as f:
        data = f.read()
    
    targets = [
        ("Let's draw a smile (Ahmed's daughter)", 21),
        ("Rania", 164),
        ("Mohammed  Suhail", 111),
        ("Fayez", 895),
        ("Ibtisam", 410),
        ("Mahmoud Basem", 492),
        ("Samirah", 350)
    ]
    
    main_headers = get_row_data(data, "Main", 1)

    for s_name, r_idx in targets:
        headers = get_row_data(data, s_name, 1) or main_headers
        row = get_row_data(data, s_name, r_idx)
        print(f"\n--- {s_name} Row {r_idx} ---")
        if not row:
            print("Row not found")
            continue
        # Print only A-AZ
        for i in range(52):
            col = idx_to_col(i)
            if col in row:
                print(f"  {col}({headers.get(col, '')}): {row[col]}")

    # Check Main sheet column AB for a few rows
    print("\n--- Main Sheet Column AB Check ---")
    for r in [1, 10, 100, 500, 1000]:
        row = get_row_data(data, "Main", r)
        if row and 'AB' in row:
            print(f"  Row {r} AB: {row['AB']}")
        elif row:
            print(f"  Row {r} AB: EMPTY")
