import zipfile
import re
import os

def audit_total2():
    ods_path = 'total2_copy.ods'
    if not os.path.exists(ods_path):
        print(f"{ods_path} not found.")
        return

    print(f"Extracting {ods_path}...")
    try:
        with zipfile.ZipFile(ods_path, 'r') as z:
            content = z.read('content.xml').decode('utf-8')
            
        print("Searching for 'Samirah' in content...")
        
        # 1. List all sheets fully
        sheet_names = re.findall(r'table:name="([^"]*)"', content)
        print(f"Total Sheets: {len(sheet_names)}")
        for s in sheet_names:
            print(f"Sheet: {s}")
            
        # 2. Inspect Samirah Sheet
        target_sheet = 'Samirah'
        if target_sheet in sheet_names:
            print(f"\n--- Inspecting contents of sheet: {target_sheet} ---")
            sheet_start = content.find(f'table:name="{target_sheet}"')
            sheet_end = content.find('</table:table>', sheet_start)
            sheet_xml = content[sheet_start:sheet_end]
            
            rows = re.findall(r'<table:table-row.*?>(.*?)</table:table-row>', sheet_xml, re.DOTALL)
            print(f"Rows found: {len(rows)}")
            
            # Print first 20 rows
            for i, row in enumerate(rows[:20]):
                # expand text:p
                cells = []
                raw_cells = re.findall(r'<table:table-cell.*?>(.*?)</table:table-cell>', row, re.DOTALL)
                for c in raw_cells:
                    txt = re.findall(r'<text:p>(.*?)</text:p>', c)
                    val = re.findall(r'office:value="([^"]*)"', c)
                    
                    if txt: cells.append(txt[0])
                    elif val: cells.append(f"[{val[0]}]")
                    else: cells.append("")
                
                print(f"Row {i+1}: {cells}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    audit_total2()
