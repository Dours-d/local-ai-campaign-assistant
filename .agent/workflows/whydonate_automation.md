---
description: Whydonate automation and creation finality
---

// turbo-all

1. Prepare the batch queue from submissions
   `python scripts/prepare_whydonate_batch.py`

2. Run the Whydonate Automater
   `python scripts/whydonate_batch_automater.py`

3. Reconcile and Finalize (Update Unified DB)
   `python scripts/whydonate_reconcile_all.py`

4. Generate Distribution Messages (Finality)
   `python scripts/generate_onboarding_messages.py`
