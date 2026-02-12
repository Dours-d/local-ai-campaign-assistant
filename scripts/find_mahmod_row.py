import re
import os

if __name__ == "__main__":
    content_path = 'temp_total2/content.xml'
    with open(content_path, 'r', encoding='utf-8', errors='ignore') as f:
        data = f.read()

    # Find Main
    start = data.find('table:name="Main"')
    if start == -1:
        print("Main sheet not found")
        exit()
        
    end = data.find('</table:table>', start)
    table_xml = data[start:end]

    rows = list(re.finditer(r'<table:table-row.*?>(.*?)</table:table-row>', table_xml, re.DOTALL))
    
    for i, r in enumerate(rows):
        if 'Help Mahmod' in r.group(1):
            print(f"FOUND MAHMOD AT ROW {i+1} (1-indexed)")
            # Print content of first 500 chars to check
            # print(r.group(1)[:500])
            break
