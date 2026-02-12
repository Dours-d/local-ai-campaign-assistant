import zipfile
import re
import xml.etree.ElementTree as ET

ODS_FILE = "total2_copy.ods"

def find_hints():
    try:
        with zipfile.ZipFile(ODS_FILE, 'r') as z:
            with z.open('content.xml') as f:
                content = f.read().decode('utf-8')
                
                # Check for "Samirah" sheet specifically
                print("--- Inspecting Sheets for Hints ---")
                root = ET.fromstring(content)
                for sheet in root.findall('.//{urn:oasis:names:tc:opendocument:xmlns:table:1.0}table'):
                    sheet_name = sheet.get('{urn:oasis:names:tc:opendocument:xmlns:table:1.0}name')
                    if sheet_name in ["Samirah", "Main", "noor"]:
                        print(f"\nSheet: {sheet_name}")
                        
                        rows = sheet.findall('.//{urn:oasis:names:tc:opendocument:xmlns:table:1.0}table-row')
                        for r_idx, row in enumerate(rows[:100]): # First 100 rows
                            for c_idx, cell in enumerate(row.findall('.//{urn:oasis:names:tc:opendocument:xmlns:table:1.0}table-cell')):
                                # 1. Get Text
                                ps = cell.findall('.//{urn:oasis:names:tc:opendocument:xmlns:text:1.0}p')
                                cell_text = " ".join([t.text for t in ps if t.text]).strip()
                                
                                # 2. Get Annotations
                                annotations = cell.findall('.//{urn:oasis:names:tc:opendocument:xmlns:office:1.0}annotation')
                                comment_text = ""
                                for ann in annotations:
                                    ann_ps = ann.findall('.//{urn:oasis:names:tc:opendocument:xmlns:text:1.0}p')
                                    comment_text += " ".join([t.text for t in ann_ps if t.text])
                                
                                if comment_text or any(k in cell_text for k in ["!", "Expected", "=", "$"]):
                                    print(f"  [R{r_idx+1}C{c_idx+1}] Val: '{cell_text}' | Comment: '{comment_text.strip()}'")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_hints()
