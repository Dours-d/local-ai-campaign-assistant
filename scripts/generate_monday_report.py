
import json
import os
from datetime import datetime

LEDGER_FILE = "data/internal_ledger.json"
REPORT_OUTPUT = "data/reports/monday_report_latest.md"

def generate_report():
    if not os.path.exists(LEDGER_FILE):
        print("Error: Ledger file not found. Run scripts/reconcile_ledger.py first.")
        return

    with open(LEDGER_FILE, 'r', encoding='utf-8') as f:
        ledger = json.load(f)

    today = datetime.now().strftime("%Y-%m-%d")
    
    total_gross = sum(d['raised_gross_eur'] for d in ledger.values())
    total_net_raised = sum(d['raised_gross_eur'] - d['sustainability_fees_eur'] - d['stripe_fx_fees_eur'] for d in ledger.values())
    total_sustainability = sum(d['sustainability_fees_eur'] for d in ledger.values())
    total_fx = sum(d['stripe_fx_fees_eur'] for d in ledger.values())
    total_payouts = sum(d['payouts_completed_eur'] for d in ledger.values())
    total_remaining = total_net_raised - total_payouts

    report = f"""# Monday Transparency Report: Gaza Resilience Fund
**Date**: {today}

## 📊 Global Summary
| Metric | Amount (EUR) |
| :--- | :--- |
| **Total Raised (Gross)** | €{total_gross:,.2f} |
| **Stripe FX Fees (2.5%)** | €{total_fx:,.2f} |
| **Sustainability Fee (25%)** | €{total_sustainability:,.2f} |
| **Total Payouts Completed** | **€{total_payouts:,.2f}** |
| **Net Remaining for Redistribution** | **€{total_remaining:,.2f}** |

---

## 👨‍👩‍👧‍👦 Beneficiary Breakdown (Top Allocations)
*Minimum disbursement threshold: €500.00*

| ID | Gross Raised | Sustainability Fee | Payouts Done | Remaining Balance | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
"""

    # Sort by net available + payouts (total value allocated)
    sorted_ledger = sorted(ledger.items(), key=lambda x: (x[1]['net_available_eur'] + x[1]['payouts_completed_eur']), reverse=True)

    for name, data in sorted_ledger:
        if data['raised_gross_eur'] > 0:
            status = "✅ Threshold Met" if (data['net_available_eur'] + data['payouts_completed_eur']) >= 500 else "⏳ Accumulating"
            report += f"| {name} | €{data['raised_gross_eur']:.2f} | €{data['sustainability_fees_eur']:.2f} | €{data['payouts_completed_eur']:.2f} | €{data['net_available_eur']:.2f} | {status} |\n"

    report += """
---

## 🛡️ Sovereign Principles Reminder
1. **Isolation Policy**: We do not interact with Chuffed/Stripe APIs to prevent further freezes. All data is derived from offline exports.
2. **Zero-Waste**: Funds are batch-payout in €500 units to avoid bank transfer fees ($20/wire).
3. **Auditability**: This report is generated deterministically from the `internal_ledger.json`.

---
*End of Report*
"""

    os.makedirs(os.path.dirname(REPORT_OUTPUT), exist_ok=True)
    with open(REPORT_OUTPUT, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"Monday Report generated at: {REPORT_OUTPUT}")

if __name__ == "__main__":
    generate_report()
