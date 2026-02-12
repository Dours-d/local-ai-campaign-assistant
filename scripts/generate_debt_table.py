import sys
import os
import io
import re

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

import scripts.final_dump_fixed as d

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def get_all_debts():
    # Return list of {campaign, amount, hint}
    debts_list = []
    
    # 1. Static Verified Debts (Name, Amount)
    # hints help map to ledger names
    static_debts = [
        ("Help Mahmod rebuild his life and support his family in Gaza", 2992.19, "Mahmoud-002"), # Mahmoud-002 (Pioneer Gross Value)
        ("Help Rania and her daughters survive in Gaza", 385.03, "Rania"),
        ("Help Fayez and his family rebuild their lives", 300.00, "Fayezs"),
        ("Help Mohammed Suhail verify his debt", 164.66, "Mohammed-011"), # Map to specific Mohammed
        ("Help Zina and her Family rebuild their lives in Gaza Palestine.", 18.00, "Zina-001"),
        ("Help Hala and her family rebuild their lives in Gaza", 216.00, "Hala-002"),
        ("Help Samirah and her Family rebuild their lives & Palestine", 405.57, "Samirah")
    ]
    
    for title, amt, hint in static_debts:
        debts_list.append({"campaign": title, "amount": amt, "hint": hint})
    
    # 2. Process Noor Sheet (Rows 2-70)
    try:
        with open('temp_total2/content.xml', 'r', encoding='utf-8', errors='ignore') as f:
            xml_data = f.read()

        # Find sheet name matching "Noor"
        sheet_names = re.findall(r'table:name="([^"]*)"', xml_data)
        noor_sheet = None
        for name in sheet_names:
            if 'noor' in name.lower():
                noor_sheet = name
                break
                
        if noor_sheet:
            for i in range(2, 71): # Rows 2 to 70 (User specified)
                row_vals = d.get_row_values(xml_data, noor_sheet, i)
                if not row_vals: continue
                
                try:
                    amt = float(row_vals.get('E', '0').replace(',', ''))
                except:
                    amt = 0.0
                    
                campaign = row_vals.get('A', 'Unknown Campaign')
                campaign = campaign.strip()
                
                if amt > 0:
                    # Dedupe with static? (Simple check)
                    existing = next((item for item in debts_list if item["campaign"] == campaign), None)
                    if existing:
                        existing["amount"] += amt
                    else:
                        # Specific Maps
                        if "Help Noor's Family Escape Gaza" in campaign: hint = "Noor-001"
                        elif "Help Hanin support her family" in campaign: hint = "Hanin-003"
                        elif "Help Ibtisam and her family surviving" in campaign: hint = "Ibtisam-003"
                        elif "Help Ibtisam survive" in campaign: hint = "Ibtisam-004"
                        elif "Help Khaled and his family rebuild" in campaign: hint = "Khaled-003"
                        elif "Help Rami Odeh" in campaign: hint = "Rami"
                        elif "Help sister Lian" in campaign: hint = "Lian"
                        elif "Help Hassan survive" in campaign: hint = "Hassan"
                        elif "Help Walid Ashour" in campaign: hint = "Walid"
                        elif "Help Hisham surpass" in campaign: hint = "Hisham-001"
                        elif "Help Khaled Yahya" in campaign: hint = "Khaled-001"
                        
                        # Generic / Fallback
                        elif "Rania" in campaign: hint = "Rania"
                        elif "Fayez" in campaign: hint = "Fayezs"
                        elif "Mahmod" in campaign: hint = "Mahmoud-002"
                        elif "Suhail" in campaign: hint = "Mohammed-011"
                        elif "Zina" in campaign: hint = "Zina-001"
                        elif "Hala" in campaign: hint = "Hala-002"
                        else:
                            hint = "Unmapped"
                        
                        debts_list.append({"campaign": campaign, "amount": amt, "hint": hint})

    except Exception as e:
        print(f"Error reading Noor sheet: {e}", file=sys.stderr)
    
    return debts_list

def main():
    debts = get_all_debts()
    
    # 3. Output Table
    print("| Campaign Title | Beneficiary / Source | Outstanding Debt (EUR) |")
    print("| :--- | :--- | :--- |")
    
    # Sort by amount desc
    sorted_debts = sorted(debts, key=lambda x: x['amount'], reverse=True)
    
    total_all = 0.0
    
    for item in sorted_debts:
        camp = item['campaign']
        amt = item['amount']
        hint = item['hint']
        
        if amt < 0.01: continue

        print(f"| {camp} | {hint} | {amt:,.2f} |")
        total_all += amt
        
    print(f"| **TOTAL** | | **{total_all:,.2f}** |")

if __name__ == "__main__":
    main()
