import pandas as pd
import os

ODS_FILE = "total2_copy.ods"

def inspect_ods():
    if not os.path.exists(ODS_FILE):
        print(f"File not found: {ODS_FILE}")
        return

    try:
        # Load the spreadsheet
        xls = pd.ExcelFile(ODS_FILE, engine='odf')
        print(f"Sheets found: {xls.sheet_names}")
        
        # Check if any sheet looks like a mapping
        for sheet in xls.sheet_names:
            print(f"\n--- Sheet: {sheet} ---")
            df = pd.read_excel(xls, sheet_name=sheet, nrows=5)
            print(df.columns.tolist())
            print(df.head())
            
    except Exception as e:
        print(f"Error reading ODS: {e}")

if __name__ == "__main__":
    inspect_ods()
