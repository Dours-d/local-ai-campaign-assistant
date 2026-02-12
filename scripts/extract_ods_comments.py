from odf.opendocument import load
from odf.table import Table, TableRow, TableCell
from odf.text import P
from odf.office import Annotation
import os

ODS_FILE = "total2_copy.ods"

def extract_comments():
    if not os.path.exists(ODS_FILE):
        print(f"File not found: {ODS_FILE}")
        return

    try:
        doc = load(ODS_FILE)
        print(f"Loaded {ODS_FILE}")
        
        found_any = False
        for sheet in doc.spreadsheet.getElementsByType(Table):
            sheet_name = sheet.getAttribute("name")
            print(f"\nChecking Sheet: {sheet_name}")
            
            rows = sheet.getElementsByType(TableRow)
            for r_idx, row in enumerate(rows):
                cells = row.getElementsByType(TableCell)
                for c_idx, cell in enumerate(cells):
                    # Annotations/Comments are usually in office:annotation
                    annotations = cell.getElementsByType(Annotation)
                    if annotations:
                        # Get cell value for context
                        cell_val = ""
                        ps = cell.getElementsByType(P)
                        if ps:
                            cell_val = "".join([node.firstChild.data for node in ps if node.firstChild and hasattr(node.firstChild, 'data')])
                        
                        for ann in annotations:
                            # Get the text inside the annotation
                            ann_ps = ann.getElementsByType(P)
                            comment_text = " ".join(["".join([n.firstChild.data for n in p.childNodes if n.firstChild and hasattr(n.firstChild, 'data')]) for p in ann_ps])
                            
                            if comment_text.strip():
                                print(f"  [Cell {r_idx+1},{c_idx+1}] Value: '{cell_val}' | Comment: {comment_text}")
                                found_any = True
                                
        if not found_any:
            print("No comments/annotations found in any sheet.")
            
    except Exception as e:
        print(f"Error reading ODS comments: {e}")

if __name__ == "__main__":
    extract_comments()
