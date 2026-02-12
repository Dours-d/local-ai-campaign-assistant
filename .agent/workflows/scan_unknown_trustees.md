---
description: Workflow for identifying and onboarding potential trustees from WhatsApp exports.
---

This workflow automates the discovery, identity management, and onboarding for new potential trustees found in WhatsApp data.

1. **Discovery Scan**
   - Run `discover_missing_contacts.py` to identify unique phone numbers in the exports.
   - Strictly filters for international codes: +972 (Israel), +970 (Palestine), +967 (Yemen).
   - Performs deep redundancy check against `campaigns_unified.json` and `potential_beneficiaries.json`.
   ```pwsh
   python scripts/discover_missing_contacts.py
   ```
   - *Output: data/potential_growth_list.json*

2. **Rationality Audit**
   - Perform a manual or automated audit to remove noise and non-human contacts.
   ```pwsh
   python scripts/rationality_audit.py
   ```
   - *Input: data/potential_growth_list.json*
   - *Output: data/potential_growth_list_audited.json*

3. **Numbered Identity Assignment**
   - Assign autonomous identities (e.g., "Trustee 001") to audited contacts.
   ```pwsh
   python scripts/assign_numbered_identities.py
   ```
   - *Note: Normalizes existing names to use spaces and creates purely numeric IDs for técnicos.*
   - *Output: data/potential_growth_list_final.json*

4. **Joint Message Generation**
   - Generate joint Arabic and English onboarding messages.
   ```pwsh
   python scripts/generate_growth_messages.py
   ```
   - *Provisions USDT-TRC20 wallets and creates single joint files.*
   - *Result: Joint files in data/onboarding_outbox/ (e.g., "Trustee 001 onboarding.txt")*

5. **Final Review & Dispatch**
   - Review the messages and dispatch to the respective contacts.
