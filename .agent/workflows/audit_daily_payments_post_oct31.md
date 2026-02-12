---
description: Daily payment status audit for donation events from October 31st onwards.
---

This workflow defines the procedure for tracking and defining the status of donation events occurring on or after 2025-10-31, primarily using the `payments!` sheet in `Daily.ods`.

1. **Daily Dataset Extraction**
   - Extract the `payments!` sheet from `GGF/Daily.ods`.
   - Filter for rows with timestamps on or after **2025-10-31**.

2. **Daily Trustee Mapping**
   - Map identified donation events to WhatsApp numbers using the `scripts/orphan_donation_audit.py` mapping logic.
   - Aggregate daily totals per trustee to ensure consistency with `Daily` ledger reporting.

3. **Status Definition**
   - Define status (e.g., `Collected`, `Pending Payout`, `Sent to Trustee`) based on the multi-column metrics in `Daily.ods`.
   - Update the `internal_ledger.json` with these high-fidelity daily increments.

4. **Message Generation**
   - Generate distribution messages for trustees based on the daily audit results.
   - Reconcile with the `chuffed_id` or `stripe_id` captured in the daily payments list.
