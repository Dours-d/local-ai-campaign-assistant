import zipfile
import xml.etree.ElementTree as ET

ODS_FILE = "total2_copy.ods"

def list_sheets():
    try:
        with zipfile.ZipFile(ODS_FILE, 'r') as z:
            with z.open('content.xml') as f:
                tree = ET.parse(f)
                root = tree.getroot()
                
                # Namespaces
                ns = {
                    'table': 'urn:oasis:names:tc:opendocument:xmlns:table:1.0',
                    'office': 'urn:oasis:names:tc:opendocument:xmlns:office:1.0'
                }
                
                sheets = root.findall('.//table:table', ns)
                print(f"Sheets in {ODS_FILE}:")
                for s in sheets:
                    print(f"  - {s.get('{urn:oasis:names:tc:opendocument:xmlns:table:1.0}name')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_sheets()
