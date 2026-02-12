import zipfile
import re
import xml.etree.ElementTree as ET

ODS_FILE = "total2_copy.ods"

def find_all_clues():
    try:
        with zipfile.ZipFile(ODS_FILE, 'r') as z:
            with z.open('content.xml') as f:
                content = f.read().decode('utf-8')
                
                # Namespaces
                ns = {
                    'table': 'urn:oasis:names:tc:opendocument:xmlns:table:1.0',
                    'office': 'urn:oasis:names:tc:opendocument:xmlns:office:1.0',
                    'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0'
                }
                
                # 1. Broad Regex for any office:annotation
                print("--- Searching for office:annotation ---")
                annotations = re.findall(r'<office:annotation.*?</office:annotation>', content, re.DOTALL)
                for i, ann in enumerate(annotations):
                    texts = re.findall(r'<text:p[^>]*>(.*?)</text:p>', ann, re.DOTALL)
                    clean_text = " ".join(texts)
                    clean_text = re.sub(r'<[^>]+>', '', clean_text)
                    if clean_text.strip():
                        print(f"Comment {i+1}: {clean_text.strip()}")

                # 2. Search for common keywords "Expected", "Raised", "Debt", "Paid"
                print("\n--- Searching for Keywords in Cells ---")
                root = ET.fromstring(content)
                for sheet in root.findall('.//{urn:oasis:names:tc:opendocument:xmlns:table:1.0}table'):
                    sheet_name = sheet.get('{urn:oasis:names:tc:opendocument:xmlns:table:1.0}name')
                    if sheet_name.lower() == 'debts':
                        continue # DISCARD DEBTS TAB
                        
                    for r_idx, row in enumerate(sheet.findall('.//{urn:oasis:names:tc:opendocument:xmlns:table:1.0}table-row')):
                        for c_idx, cell in enumerate(row.findall('.//{urn:oasis:names:tc:opendocument:xmlns:table:1.0}table-cell')):
                            cell_text = "".join([t.text for t in cell.findall('.//{urn:oasis:names:tc:opendocument:xmlns:text:1.0}p') if t.text])
                            if any(k in cell_text for k in ["Expected", "Raised", "Debt", "Paid", "Calculus"]):
                                print(f"[{sheet_name}] Cell R{r_idx+1}C{c_idx+1}: {cell_text}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_all_clues()
