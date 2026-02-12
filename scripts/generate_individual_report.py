
import json
import os
from datetime import datetime
import sys

# Ensure we can import sibling scripts
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import generate_debt_table as debt_source

# Paths
LEDGER_FILE = "data/internal_ledger.json"
REGISTRY_FILE = "data/campaign_registry.json"
INDEX_FILE = "data/campaign_index.json"
REPORTS_DIR = "data/reports/individual"

THRESHOLD = 100.0  # EUR

def load_json(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def generate_reports():
    ledger = load_json(LEDGER_FILE)
    registry = load_json(REGISTRY_FILE).get("mappings", {})
    index = load_json(INDEX_FILE)
    
    # Load Verified Debts to ensure Rational Reporting
    debts_list = debt_source.get_all_debts()
    debt_map = {}
    
    HINT_TO_KEY = {
        "Mahmoud-002": "Mahmoud-002",
        "Mahmoud": "Mahmoud-002",
        "Mahmod": "Mahmoud-002",
        "Noor-001": "Noor-001",
        "Noor": "Noor-001",
        "Mohammed": "Mohammed-011",
        "Mohammed-011": "Mohammed-011",
        "Suhail": "Mohammed-011",
        "Zina": "Zina-001",
        "Zina-001": "Zina-001",
        "Hala": "Hala-002",
        "Hala-002": "Hala-002",
        "Rania": "Rania",
        "Fayezs": "Fayezs",
        "Fayez": "Fayezs",
        "Samirah": "Samirah"
    }

    for item in debts_list:
        hint = item['hint']
        amt = item['amount']
        matched_key = HINT_TO_KEY.get(hint)
        if not matched_key:
            for l_key in ledger.keys():
                if l_key.lower().startswith(hint.lower()):
                    matched_key = l_key
                    break
        if matched_key:
            debt_map[matched_key] = debt_map.get(matched_key, 0.0) + amt

    os.makedirs(REPORTS_DIR, exist_ok=True)
    
    # Reverse index to map campaign IDs back to WhatsApp
    cid_to_whatsapp = {}
    for wa, p_data in index.items():
        if "chuffed" in p_data:
            cid_to_whatsapp[f"chuffed_{p_data['chuffed']['id']}"] = wa

    summary = []

    for beneficiary_name, data in ledger.items():
        # financial metrics
        gross = data.get("raised_gross_eur", 0.0)
        sust_fees = data.get("sustainability_fees_eur", 0.0)
        stripe_fees = data.get("stripe_fx_fees_eur", 0.0)
        ledger_unpaid = data.get("unpaid_balance_eur", 0.0)
        
        # Payout/Balance Override
        verified_gross = debt_map.get(beneficiary_name, 0.0)
        payout_override = 0.0
        if beneficiary_name == "Mahmoud-002":
            payout_override = 2776.49
            
        net_available = gross - (sust_fees + stripe_fees)
        payouts = (net_available - ledger_unpaid) + payout_override
        if payouts < 0: payouts = 0.0
        
        # Pending Balance (Net)
        unpaid = verified_gross - payouts
        if unpaid < 0: unpaid = 0.0
        
        campaign_ids = data.get("campaigns", [])
        
        # Identity match
        whatsapp = "Unknown"
        wallet = "Unknown"
        for r_id, r_data in registry.items():
            if r_data.get("name") == beneficiary_name:
                whatsapp = r_data.get("whatsapp") or whatsapp
                wallet = r_data.get("wallet_address") or wallet
                break
        
        if whatsapp == "Unknown":
            for cid in campaign_ids:
                if cid in cid_to_whatsapp:
                    whatsapp = cid_to_whatsapp[cid]
                    for r_id, r_data in registry.items():
                        if r_data.get("whatsapp") == whatsapp:
                            wallet = r_data.get("wallet_address") or wallet
                            break
                    break
        
        # Status Logic
        if unpaid <= 0.01:
            status = "EQUALIZED"
        elif payouts > 0:
            status = "PAID (Partial)"
        elif unpaid >= THRESHOLD:
            status = "READY (Payout Pending)"
        else:
            status = "COLLECTING (Below Threshold)"

        report = {
            "beneficiary": beneficiary_name,
            "status": status,
            "financials": {
                "raised_gross_eur": gross,
                "total_fees_eur": sust_fees + stripe_fees,
                "payouts_completed_eur": payouts,
                "unpaid_balance_eur": unpaid
            }
        }

        # Write individual markdown report
        md_content = f"""# Individual Status Report: {beneficiary_name}
Generated on: {datetime.now().strftime('%Y-%m-%d')}

## 1. Identity & Contact
- **WhatsApp**: {whatsapp}
- **Wallet**: `{wallet}`
- **Current Status**: **{status}**

## 2. Financial History (EUR)
| Metric | Amount |
|--------|--------|
| **Gross Raised** | €{gross:.2f} |
| **Fees (Sustainability + FX)** | €{sust_fees + stripe_fees:.2f} |
| **Net Available** | €{net_available:.2f} |
| **Total Paid Out** | €{payouts:.2f} |
| **Pending Balance** | **€{unpaid:.2f}** |

## 3. Equalization Projection
"""
        if status == "EQUALIZED":
            md_content += "All funds have been successfully disbursed. No outstanding balance.\n"
        elif status == "READY (Payout Pending)":
            md_content += f"The balance of €{unpaid:.2f} exceeds the €100 threshold. A disbursement is scheduled for the next payment cycle.\n"
        elif status == "COLLECTING (Below Threshold)":
            needed = max(0, THRESHOLD - unpaid)
            md_content += f"Active collection. €{needed:.2f} more needed to reach the €100 disbursement threshold.\n"
        else:
            md_content += "Processing ongoing.\n"

        file_name = f"{beneficiary_name.replace(' ', '_')}_report.md"
        with open(os.path.join(REPORTS_DIR, file_name), 'w', encoding='utf-8') as f:
            f.write(md_content)
            
        summary.append(report)

    with open(os.path.join(REPORTS_DIR, "index.json"), 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)

    # Cleanup Stale Reports
    current_files = set(f"{r['beneficiary'].replace(' ', '_')}_report.md" for r in summary)
    current_files.add("index.json")
    
    deleted_count = 0
    if os.path.exists(REPORTS_DIR):
        for f_name in os.listdir(REPORTS_DIR):
            if f_name.endswith("_report.md") and f_name not in current_files:
                try:
                    os.remove(os.path.join(REPORTS_DIR, f_name))
                    deleted_count += 1
                except OSError:
                    pass

    print(f"Generated {len(summary)} individual reports.")
    if deleted_count > 0:
        print(f"Cleaned up {deleted_count} stale/non-compliant report files.")

if __name__ == "__main__":
    generate_reports()
