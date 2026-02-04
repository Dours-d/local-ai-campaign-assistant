
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
    
    # 1. Load Unified DB to map IDs to Internal Names
    with open(UNIFIED_DB, 'r', encoding='utf-8') as f:
        unified_data = json.load(f)
        id_to_internal = {c['id']: c['privacy']['internal_name'] for c in unified_data['campaigns']}
        # Populate ledger with all internal names
        for internal_name in set(id_to_internal.values()):
            ledger[internal_name] = {
                "raised_gross_eur": 0.0,
                "stripe_fx_fees_eur": 0.0,
                "sustainability_fees_eur": 0.0,
                "net_available_eur": 0.0,
                "payouts_completed_eur": 0.0,
                "campaigns": []
            }

    # 2. Process Chuffed CSVs
    csv_files = glob.glob(os.path.join(REPORTS_DIR, "*.csv"))
    for csv_path in csv_files:
        campaign_id_raw = os.path.basename(csv_path).replace(".csv", "")
        campaign_id = f"chuffed_{campaign_id_raw}"
        internal_name = id_to_internal.get(campaign_id)
        
        if not internal_name:
            continue
            
        if campaign_id not in ledger[internal_name]["campaigns"]:
            ledger[internal_name]["campaigns"].append(campaign_id)

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    amount = float(row.get('Donation', 0))
                    currency = row.get('Currency', 'EUR')
                    
                    # Convert to EUR and track Stripe FX fee
                    gross_eur = CurrencyConverter.convert_to_eur(amount, currency)
                    fx_fee = CurrencyConverter.get_fee(amount, currency)
                    
                    ledger[internal_name]["raised_gross_eur"] += gross_eur
                    ledger[internal_name]["stripe_fx_fees_eur"] += fx_fee
                except:
                    continue

    # 3. Process Whydonate (Mocked as we'd need their export format, but using unified DB stats for now)
    for campaign in unified_data['campaigns']:
        if campaign['platform'] == 'whydonate':
            internal_name = campaign['privacy']['internal_name']
            # Whydonate typically is in EUR or translates to it easily
            raised = campaign.get('raised_eur', 0)
            ledger[internal_name]["raised_gross_eur"] += raised
            if campaign['id'] not in ledger[internal_name]["campaigns"]:
                ledger[internal_name]["campaigns"].append(campaign['id'])

    # 4. Process LaunchGood (Umbrella) CSVs
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
                            ledger[internal_name]["raised_gross_eur"] += gross_eur
                            ledger[internal_name]["stripe_fx_fees_eur"] += fx_fee
                            assigned = True
                            break
                    
                    if not assigned:
                        unassigned_pool_eur += (gross_eur - fx_fee)
                except:
                    continue

    # 5. Process Completed Payouts
    PAYOUTS_FILE = "data/payouts_completed.json"
    if os.path.exists(PAYOUTS_FILE):
        with open(PAYOUTS_FILE, 'r', encoding='utf-8') as f:
            payouts = json.load(f)
            for p in payouts:
                beneficiary_id = p.get('beneficiary_id')
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

    # 6. Final Calculations (Sustainability Fee & Net)
    for name, data in ledger.items():
        data["sustainability_fees_eur"] = data["raised_gross_eur"] * SUSTAINABILITY_FEE
        data["net_available_eur"] = data["raised_gross_eur"] - data["sustainability_fees_eur"] - data["payouts_completed_eur"]
        
        # Rounding for cleanliness
        data["raised_gross_eur"] = round(data["raised_gross_eur"], 2)
        data["stripe_fx_fees_eur"] = round(data["stripe_fx_fees_eur"], 2)
        data["sustainability_fees_eur"] = round(data["sustainability_fees_eur"], 2)
        data["payouts_completed_eur"] = round(data["payouts_completed_eur"], 2)
        data["net_available_eur"] = round(data["net_available_eur"], 2)

    # 7. Save Ledger
    with open(OUTPUT_LEDGER, 'w', encoding='utf-8') as f:
        json.dump(ledger, f, indent=2)
    
    print(f"Sovereign Ledger reconciled: {len(ledger)} beneficiaries tracked.")
    total_net = sum(d['net_available_eur'] for d in ledger.values())
    print(f"Total Net Available toward aid: €{total_net:,.2f}")
    print(f"Unassigned General Pool: €{unassigned_pool_eur:,.2f} (To be distributed by need)")
    with open(OUTPUT_LEDGER, 'w', encoding='utf-8') as f:
        json.dump(ledger, f, indent=2)
    
    print(f"Sovereign Ledger reconciled: {len(ledger)} beneficiaries tracked.")
    total_net = sum(d['net_available_eur'] for d in ledger.values())
    print(f"Total Net Available toward aid: €{total_net:,.2f}")

if __name__ == "__main__":
    reconcile()
