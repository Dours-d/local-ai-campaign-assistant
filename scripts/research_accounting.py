import os
import sys
import re
import pandas as pd
from odf.opendocument import load
from odf.table import Table, TableRow, TableCell
from odf.text import P

GGF_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'GGF')

def search_ods(file_path, query):
    results = []
    try:
        doc = load(file_path)
        for sheet in doc.spreadsheet.getElementsByType(Table):
            sheet_name = sheet.getAttribute("name")
            for r_idx, row in enumerate(sheet.getElementsByType(TableRow)):
                for c_idx, cell in enumerate(row.getElementsByType(TableCell)):
                    ps = cell.getElementsByType(P)
                    text = " ".join([ET.tostring(p, encoding='unicode', method='text') for p in ps]).strip()
                    if query.lower() in text.lower():
                        results.append({
                            "file": os.path.basename(file_path),
                            "sheet": sheet_name,
                            "cell": f"R{r_idx+1}C{c_idx+1}",
                            "text": text
                        })
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return results

def search_csv(file_path, query):
    results = []
    try:
        df = pd.read_csv(file_path)
        for idx, row in df.iterrows():
            row_text = " ".join(row.astype(str))
            if query.lower() in row_text.lower():
                results.append({
                    "file": os.path.basename(file_path),
                    "row": idx + 1,
                    "text": row_text
                })
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return results

def main():
    if len(sys.argv) < 2:
        print("Usage: python research_accounting.py <query>")
        return

    query = sys.argv[1]
    print(f"--- Researching GGF Accounting Data for: '{query}' ---")

    for filename in os.listdir(GGF_DIR):
        file_path = os.path.join(GGF_DIR, filename)
        if filename.endswith(".ods"):
            # ODS searching is slow with odfpy, maybe just use simple keywords for now or pandas if possible
            # But odfpy is more reliable for values inside cells sometimes.
            # Let's try pandas first for speed
            try:
                xl = pd.ExcelFile(file_path, engine='odf')
                for sheet in xl.sheet_names:
                    df = xl.parse(sheet)
                    for idx, row in df.iterrows():
                        row_text = " ".join([str(x) for x in row])
                        if query.lower() in row_text.lower():
                            print(f"[ODS] {filename} | Sheet: {sheet} | Row: {idx+2}")
                            print(f" > {row_text[:200]}...")
            except Exception as e:
                print(f"Error reading ODS {filename}: {e}")
        elif filename.endswith(".csv"):
            try:
                df = pd.read_csv(file_path)
                for idx, row in df.iterrows():
                    row_text = " ".join([str(x) for x in row])
                    if query.lower() in row_text.lower():
                        print(f"[CSV] {filename} | Row: {idx+1}")
                        print(f" > {row_text[:200]}...")
            except Exception as e:
                print(f"Error reading CSV {filename}: {e}")

if __name__ == "__main__":
    main()
