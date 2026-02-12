
import json
import os

LEDGER_FILE = "data/internal_ledger.json"

def generate_report():
    if not os.path.exists(LEDGER_FILE):
        print("Error: Ledger file not found.")
        return

    with open(LEDGER_FILE, 'r', encoding='utf-8') as f:
        ledger = json.load(f)

    print("\n" + "="*50)
    print(" SOVEREIGN AID FINANCIAL CONSOLIDATION REPORT")
    print("="*50)

    total_gross = 0
    total_fees = 0
    total_payouts = 0
    total_unpaid = 0
    
    chuffed_total = 0
    whydonate_total = 0
    launchgood_total = 0

    unpaid_list = []

    for name, data in ledger.items():
        total_gross += data['raised_gross_eur']
        total_fees += data['sustainability_fees_eur']
        total_payouts += data['payouts_completed_eur']
        total_unpaid += data['unpaid_balance_eur']
        
        chuffed_total += data.get('chuffed_raised_eur', 0)
        whydonate_total += data.get('whydonate_raised_eur', 0)
        launchgood_total += data.get('launchgood_raised_eur', 0)

        if data['unpaid_balance_eur'] > 0:
            unpaid_list.append((name, data['unpaid_balance_eur']))

    # Sort unpaid list by debt amount
    unpaid_list.sort(key=lambda x: x[1], reverse=True)

    print(f"\n[SUMMARY TOTALS]")
    print(f"Total Presumed Raised (Gross):  €{total_gross:,.2f}")
    print(f"Total Sustainability Fees:     -€{total_fees:,.2f}")
    print(f"Total Donations Paid (Actual): -€{total_payouts:,.2f}")
    print(f"Total Outstanding Debt:         €{total_unpaid:,.2f}")

    print(f"\n[PLATFORM BREAKDOWN]")
    print(f"Chuffed (Presumed):             €{chuffed_total:,.2f}")
    print(f"WhyDonate:                      €{whydonate_total:,.2f}")
    print(f"LaunchGood (Umbrella):          €{launchgood_total:,.2f}")

    print(f"\n[TOP 15 UNPAID BALANCES]")
    print(f"{'Beneficiary':<20} | {'Unpaid Balance':<15}")
    print("-" * 40)
    for name, balance in unpaid_list[:15]:
        print(f"{name:<20} | €{balance:>14,.2f}")

    print("\n" + "="*50)
    print(f"Total Beneficiaries with Debt: {len([x for x in unpaid_list if x[1] > 0])}")
    print("="*50 + "\n")

if __name__ == "__main__":
    generate_report()
