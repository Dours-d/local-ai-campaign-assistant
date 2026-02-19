---
description: Generating and reframing bilingual welcoming messages for beneficiaries (Amanah/Shahada).
---

This workflow is used to generate or regenerate the welcoming and campaign activation messages for beneficiaries, ensuring they are reframed with the profound concepts of **Amanah** (Trust), **Shahada** (Witness), the **Sovereign Portal**, and **Noor AI (Dunya)**.

// turbo
1. Ensure the source data in `data/potential_beneficiaries.json` and the `data/campaign_registry.json` are up to date with the latest WhyDonate URLs.

// turbo
2. Run the main message generation script to populate the outbox with reframed, bilingual messages.
```powershell
python scripts/generate_onboarding_messages.py
```

3. Verify the output in `data/onboarding_outbox/`:
   - Check that messages are bilingual (Arabic/English).
   - Ensure the **Sovereign Portal** link is correct.
   - Confirm the reference to the **Collective Umbrella Fund** and **Noor AI (Dunya)** knowledge base.

4. (Optional) If you need to apply bulk reframing to existing manual files in `data/onboarding_outbox/individual_messages/`, run the reframing utility:
```powershell
python scripts/apply_profound_reframing.py
```

5. Share the generated messages with the Trustees via WhatsApp or the preferred communication channel.
