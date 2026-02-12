import re
import sys

def audit_noor():
    try:
        with open('temp_total2/content.xml', 'r', encoding='utf-8', errors='ignore') as f:
            xml_data = f.read()

        # Find the Noor sheet start
        # <table:table table:name="Noor's Family" ... >
        match = re.search(r'<table:table table:name="([^"]*noor[^"]*)"', xml_data, re.IGNORECASE)
        if not match:
            print("Noor sheet not found")
            return
        
        sheet_name = match.group(1)
        print(f"Auditing Sheet: {sheet_name}")
        
        # Extract the table content for this sheet
        sheet_start = match.start()
        # Find the next table or end of document
        next_table = xml_data.find('<table:table ', sheet_start + 1)
        if next_table == -1:
            sheet_xml = xml_data[sheet_start:]
        else:
            sheet_xml = xml_data[sheet_start:next_table]
        
        # Find rows using a more robust regex
        rows = re.findall(r'<table:table-row.*?>.*?</table:table-row>', sheet_xml, re.DOTALL)
        print(f"Found {len(rows)} rows")
        
        summary = {}
        for i, row in enumerate(rows):
            if i < 1: continue 
            if i >= 71: break
            
            cells = re.findall(r'<table:table-cell.*?>.*?</table:table-cell>|<table:table-cell.*?/>', row, re.DOTALL)
            
            expanded_texts = []
            for cell in cells:
                rep_match = re.search(r'table:number-columns-repeated="(\d+)"', cell)
                rep = int(rep_match.group(1)) if rep_match else 1
                
                txt_match = re.search(r'<text:p>(.*?)</text:p>', cell)
                txt = txt_match.group(1).strip() if txt_match else ""
                
                # Check for office:value too
                if not txt:
                    val_match = re.search(r'office:value="([^"]*)"', cell)
                    txt = val_match.group(1) if val_match else ""
                
                expanded_texts.extend([txt] * rep)
            
            if len(expanded_texts) < 5: continue
            
            camp = expanded_texts[0]
            try:
                # Based on ROW 4 TEXTS, amount is at index 3
                amt_str = expanded_texts[3].replace(',', '')
                amt = float(amt_str) if amt_str else 0.0
            except:
                amt = 0.0
            
            if amt > 0:
                summary[camp] = summary.get(camp, 0.0) + amt
        
        print("\n--- NOOR SHEET SUMMARY ---")
        for k, v in sorted(summary.items(), key=lambda x: x[1], reverse=True):
            print(f"{k}: {v:.2f}")

        
        for k, v in sorted(summary.items(), key=lambda x: x[1], reverse=True):
            print(f"{k}: {v:.2f}")

        
        for k, v in sorted(summary.items(), key=lambda x: x[1], reverse=True):
            print(f"{k}: {v:.2f}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    audit_noor()
