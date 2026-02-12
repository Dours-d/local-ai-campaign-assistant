---
description: Investigation of unpaid donation status for Chuffed events prior to October 31st.
---

This workflow defines the procedure for auditing potential unpaid donation events identified in the legacy accounting sheets (e.g., `Total2.ods`) for the period ending 2024-10-31.

1. **Dataset Preparation**
   - Run `scripts/temporal_donation_split.py` to isolate all donation events with timestamps **before** 2025-10-31 (Note: The user clarified Chuffed timestamps until 31/10).
   
2. **Payout Cross-Referencing**
   - Cross-reference the identified events against the `Payouts` column in `Total2.ods` or corresponding bank statements.
   - Use the `scripts/reconcile_payouts.py` (or equivalent) to flag any donation with an external `Stripe` or `LaunchGood` ID that does not have a corresponding payout confirmation.

3. **Status Categorization**
   - Mark events as `Unpaid` if the funding platform reports a successful charge but no payout was received by the campaign wallet as of 31/10.
   - Separate "technical unmapped" from "confirmed unpaid" using the previously established WhatsApp mapping.

4. **Review and Escalation**
   - Generate a `pre_oct31_unpaid_audit.csv` report.
   - Escalate identities with high unpaid totals to the human trustees for manual vetting.
