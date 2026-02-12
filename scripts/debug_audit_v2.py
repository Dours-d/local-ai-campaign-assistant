import re
import os

def idx_to_col(idx):
    col = ""
    while idx >= 0:
        idx, rem = divmod(idx, 26)
        col = chr(65 + rem) + col
        idx -= 1
    return col

def dump_full_row(data, sheet_name, row_idx):
    sheet_match = re.search(f'table:name="{re.escape(sheet_name)}"', data)
    if not sheet_match:
        # Try escaped
        escaped_name = sheet_name.replace("'", "&apos;")
        sheet_match = re.search(f'table:name="{re.escape(escaped_name)}"', data)
    
    if not sheet_match:
        print(f"Sheet '{sheet_name}' not found")
        return None

    start = sheet_match.start()
    end = data.find('</table:table>', start)
    table_xml = data[start:end]
    
    rows = list(re.finditer(r'<table:table-row.*?>(.*?)</table:table-row>', table_xml, re.DOTALL))
    
    print(f"\n--- {sheet_name} ROW {row_idx} ---")
    if row_idx > len(rows):
        print(f"Row {row_idx} not found (Total: {len(rows)})")
        return
    
    row_xml = rows[row_idx-1].group(1)
    cell_pattern = re.compile(r'<(table:table-cell|table:covered-table-cell).*?(/|>(.*?)</\1)>', re.DOTALL)
    cell_matches = cell_pattern.finditer(row_xml)
    
    row_data = []
    curr_col = 0
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
        
        ann = ""
        if '<office:annotation' in cell_xml:
            ann_xml = re.search(r'<office:annotation.*?</office:annotation>', cell_xml, re.DOTALL).group(0)
            ann = " [ANN: " + " | ".join(re.findall(r'<text:p>(.*?)</text:p>', ann_xml)) + "]"

        if val.strip() or ann:
            for i in range(rep_count):
                row_data.append(f"{idx_to_col(curr_col + i)}: {val}{ann}")
        
        curr_col += rep_count
    
    # Also find if row itself is repeated
    row_tag = rows[row_idx-1].group(0)
    row_rep_match = re.search(r'table:number-rows-repeated="(\d+)"', row_tag)
    if row_rep_match:
        print(f"(Row repeated {row_rep_match.group(1)} times)")

    print(" | ".join(row_data))

if __name__ == "__main__":
    content_path = 'temp_total2/content.xml'
    with open(content_path, 'r', encoding='utf-8', errors='ignore') as f:
        data = f.read()
    
    # List of sheets to check
    sheets = [
        "Main",
        "Rania",
        "Let's draw a smile (Ahmed's daughter)",
        "Mohammed  Suhail"
    ]
    
    for s in sheets:
        dump_full_row(data, s, 1) # Headers usually at 1
        if s == "Main":
            dump_full_row(data, s, 10) # Sample campaign in Main
        if s == "Let's draw a smile (Ahmed's daughter)":
            dump_full_row(data, s, 21)
        if s == "Rania":
            dump_full_row(data, s, 164)
        if s == "Mohammed  Suhail":
            dump_full_row(data, s, 111)
