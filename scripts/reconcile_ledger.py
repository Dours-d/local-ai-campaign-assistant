
import os
import json
import csv
import glob
import sys

# Move to the project root to import our utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.utils.currency_converter import CurrencyConverter

REPORTS_DIR = "data/reports/chuffed"
LG_REPORTS_DIR = "data/reports/launchgood"
WHYDONATE_LOG = "data/whydonate_creation_log.json"
UNIFIED_DB = "data/campaigns_unified.json"
OUTPUT_LEDGER = "data/internal_ledger.json"

SUSTAINABILITY_FEE = 0.25 # 25%

def reconcile():
    ledger = {}
    
    # 1. Load Unified DB to map IDs to Internal Names and get baselines
    with open(UNIFIED_DB, 'r', encoding='utf-8') as f:
        unified_data = json.load(f)
        id_to_internal = {c['id']: c['privacy']['internal_name'] for c in unified_data['campaigns']}
        
        # Populate ledger with all internal names
        for internal_name in set(id_to_internal.values()):
            ledger[internal_name] = {
                "raised_gross_eur": 0.0,
                "chuffed_raised_eur": 0.0,
                "whydonate_raised_eur": 0.0,
                "launchgood_raised_eur": 0.0,
                "stripe_fx_fees_eur": 0.0,
                "sustainability_fees_eur": 0.0,
                "payouts_completed_eur": 0.0,
                "unpaid_balance_eur": 0.0,
                "campaigns": []
            }

    # 2. Process Platform Totals (Presumed Unpaid Baseline)
    for campaign in unified_data['campaigns']:
        internal_name = campaign['privacy']['internal_name']
        platform = campaign['platform']
        
        # Fallback Logic: Use 'unverified_summary_raised' if 'raised_eur' is 0 or low for Chuffed
        # This solves the "HTML-instead-of-CSV" reporting bug.
        raised = campaign.get('raised_eur', 0)
        unverified = campaign['attention'].get('unverified_summary_raised', 0)
        
        actual_baseline = max(raised, unverified)
        
        if platform == 'chuffed':
            ledger[internal_name]["chuffed_raised_eur"] += actual_baseline
        elif platform == 'whydonate':
            ledger[internal_name]["whydonate_raised_eur"] += actual_baseline
        
        ledger[internal_name]["raised_gross_eur"] += actual_baseline
        if campaign['id'] not in ledger[internal_name]["campaigns"]:
            ledger[internal_name]["campaigns"].append(campaign['id'])

    # 3. Process LaunchGood (Umbrella) CSVs for attribution
    lg_csv_files = glob.glob(os.path.join(LG_REPORTS_DIR, "*.csv"))
    unassigned_pool_eur = 0.0
    for csv_path in lg_csv_files:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    amount = float(row.get('Amount', 0))
                    currency = row.get('Currency', 'EUR')
                    comment = row.get('Comment', '').upper()
                    
                    gross_eur = CurrencyConverter.convert_to_eur(amount, currency)
                    fx_fee = CurrencyConverter.get_fee(amount, currency)
                    
                    # Attribution Check
                    assigned = False
                    for internal_name in ledger:
                        if internal_name.upper() in comment:
                            ledger[internal_name]["launchgood_raised_eur"] += gross_eur
                            ledger[internal_name]["raised_gross_eur"] += gross_eur
                            ledger[internal_name]["stripe_fx_fees_eur"] += fx_fee
                            assigned = True
                            break
                    
                    if not assigned:
                        unassigned_pool_eur += (gross_eur - fx_fee)
                except:
                    continue

    # 4. Process Completed Payouts
    PAYOUTS_FILE = "data/payouts_completed.json"
    if os.path.exists(PAYOUTS_FILE):
        with open(PAYOUTS_FILE, 'r', encoding='utf-8') as f:
            payouts = json.load(f)
            for p in payouts:
                beneficiary_id = p.get('beneficiary_id')
                if not beneficiary_id: continue
                
                target = None
                if beneficiary_id in ledger:
                    target = beneficiary_id
                else:
                    for name, data in ledger.items():
                        if beneficiary_id in data.get('campaigns', []):
                            target = name
                            break
                
                if target:
                    ledger[target]["payouts_completed_eur"] += float(p.get('amount_eur', 0))

    # 5. Final Calculations (Sustainability Fee & Unpaid Debt)
    for name, data in ledger.items():
        data["sustainability_fees_eur"] = data["raised_gross_eur"] * SUSTAINABILITY_FEE
        # Unpaid = (Total Platform Raised) - Fee - (What we already paid)
        data["unpaid_balance_eur"] = data["raised_gross_eur"] - data["sustainability_fees_eur"] - data["payouts_completed_eur"]
        
        # Rounding
        for key in data:
            if isinstance(data[key], float):
                data[key] = round(data[key], 2)

    # 6. Save Ledger
    with open(OUTPUT_LEDGER, 'w', encoding='utf-8') as f:
        json.dump(ledger, f, indent=2)
    
    print(f"Sovereign Ledger reconciled: {len(ledger)} beneficiaries tracked.")
    total_unpaid = sum(d['unpaid_balance_eur'] for d in ledger.values() if d['unpaid_balance_eur'] > 0)
    print(f"Total Outstanding Debt (Unpaid Aid): €{total_unpaid:,.2f}")
    print(f"Unassigned General Pool: €{unassigned_pool_eur:,.2f}")

if __name__ == "__main__":
    reconcile()
