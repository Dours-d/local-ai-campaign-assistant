import re
import os

def dump_headers_fuzzy(data, search_term):
    # Find all table names
    table_names = re.findall(r'table:name="([^"]*)"', data)
    
    match = None
    for name in table_names:
        clean_name = name.replace("&apos;", "'").replace("&quot;", '"')
        if search_term.lower() in clean_name.lower():
            match = name
            print(f"FOUND MATCHING SHEET: {match} (Search term: {search_term})")
            break
    
    if not match:
        print(f"No sheet matching '{search_term}' found")
        return

    start = data.find(f'table:name="{match}"')
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
        
        print(f"--- {match} HEADERS ---")
        print(" | ".join(row_data))

    # Also dump row 21 if it's ahmed's sheet
    if "smile" in match.lower() or "ahmed" in match.lower():
        if len(rows) >= 21:
            row_content = rows[20].group(1)
            cell_matches = cell_pattern.finditer(row_content)
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
                if val.strip():
                    for i in range(rep_count):
                        row_data.append(f"{idx_to_col(curr_col + i)}: {val}")
                curr_col += rep_count
            print(f"\n--- {match} ROW 21 ---")
            print(" | ".join(row_data))

if __name__ == "__main__":
    content_path = 'temp_total2/content.xml'
    with open(content_path, 'r', encoding='utf-8', errors='ignore') as f:
        data = f.read()
    
    dump_headers_fuzzy(data, "smile")
    dump_headers_fuzzy(data, "Main")
    dump_headers_fuzzy(data, "Rania")
    dump_headers_fuzzy(data, "Mohammed  Suhail")
