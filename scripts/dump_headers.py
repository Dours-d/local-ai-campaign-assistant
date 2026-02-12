import re
import os

def dump_headers(data, sheet_name):
    # Try different name variations
    names_to_try = [
        sheet_name,
        sheet_name.replace("'", "&apos;"),
        sheet_name.replace("'", "&quot;") # Just in case
    ]
    
    sheet_match = None
    for name in names_to_try:
        pattern = f'table:name="{name}"'
        sheet_match = re.search(pattern, data)
        if sheet_match: break
    
    if not sheet_match:
        print(f"Sheet '{sheet_name}' not found")
        return

    start = sheet_match.start()
    end = data.find('</table:table>', start)
    table_xml = data[start:end]
    
    rows = list(re.finditer(r'<table:table-row.*?>(.*?)</table:table-row>', table_xml, re.DOTALL))
    if len(rows) > 0:
        row_content = rows[0].group(1)
        cell_pattern = re.compile(r'<(table:table-cell|table:covered-table-cell).*?(/|>(.*?)</\1)>', re.DOTALL)
        cell_matches = cell_pattern.finditer(row_content)
        
        row_data = []
        curr_col = 0
        for cm in cell_matches:
            cell_xml = cm.group(0)
            rep_match = re.search(r'table:number-columns-repeated="(\d+)"', cell_xml)
            rep_count = int(rep_match.group(1)) if rep_match else 1
            
            p_match = re.search(r'<text:p>(.*?)</text:p>', cell_xml)
            val = p_match.group(1) if p_match else ""
            
            def idx_to_col(idx):
                col = ""
                while idx >= 0:
                    idx, rem = divmod(idx, 26)
                    col = chr(65 + rem) + col
                    idx -= 1
                return col

            if val:
                for i in range(rep_count):
                    row_data.append(f"{idx_to_col(curr_col + i)}: {val}")
            
            curr_col += rep_count
        
        print(f"\n--- {sheet_name} HEADERS ---")
        print(" | ".join(row_data))

if __name__ == "__main__":
    content_path = 'temp_total2/content.xml'
    with open(content_path, 'r', encoding='utf-8', errors='ignore') as f:
        data = f.read()
    
    dump_headers(data, "Let's draw a smile (Ahmed's daughter)")
    dump_headers(data, "Main")
    dump_headers(data, "Rania")
    dump_headers(data, "Mohammed  Suhail")
