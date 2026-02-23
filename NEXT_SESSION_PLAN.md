# Next Session Plan: LaunchGood & Umbrella Fund

## Current State (Context)
- **Umbrella Fund URL**: Currently set to `https://dours-d.github.io/local-ai-campaign-assistant/` (redirects to broken tunnel) as a placeholder.
- **WhyDonate**: 11 campaigns are live and working.
- **LaunchGood**: 
    - 0 individual campaigns created (all in `pending_launchgood` status).
    - Umbrella Fund campaign likely does not exist or is in draft.
    - `scripts/create_lg_umbrella_fund.py` exists but needs a valid browser session.

## Objective
Create the "Global Gaza Resilience Fund" (Umbrella Fund) on LaunchGood, then create individual sub-campaigns (if LaunchGood supports them) or simply list them within the Umbrella Fund's story, and finally update the `campaign_registry.json` and messages with the *actual* LaunchGood URL.

## Step-by-Step Plan

1.  **Browser Initialization**:
    - Start Chrome with remote debugging (port 9222).
    - Log in to LaunchGood manually.
    - Ensure the session is active.

2.  **Create Umbrella Fund**:
    - Run `python scripts/create_lg_umbrella_fund.py`.
    - Verify the campaign is created/drafted.
    - **CRITICAL**: Get the *actual* URL of this campaign (e.g., `launchgood.com/campaign/global_gaza_resilience_fund`).

3.  **Update Links (Once URL is known)**:
    - Update `script/generate_onboarding_messages.py` -> `VIRAL_URL` with the real LaunchGood URL.
    - Update `data/campaign_registry.json` -> all `launchgood_url` fields.
    - Regenerate all messages (`scripts/generate_onboarding_messages.py`, `scripts/apply_profound_reframing.py`).

4.  **Batch Create Individual Campaigns (Optional/Secondary)**:
    - If the user wants separate pages for each family on LaunchGood (similar to WhyDonate), run `python scripts/launchgood_batch_create.py`.
    - If the strategy is *only* the Umbrella Fund, skip this. **User's last comment suggests "including new created campaigns on Launchgood underneath the Umbrella fund"**, implying possibly just listing them *in* the Umbrella Fund or creating them as team members/child campaigns.
    - *Clarification*: The `create_lg_umbrella_fund.py` script *already* attempts to list all beneficiaries in the Story section of the Umbrella Fund. This might be sufficient.

5.  **Final Verification**:
    - Check the new LaunchGood link in a fresh browser context.
    - Confirm redirection/loading works.

## Technical Notes
- The `create_lg_umbrella_fund.py` script reads from `data/onboarding_submissions`. Ensure this directory has the latest JSON files (`_submission.json`).
- If `launchgood_batch_create.json` is the source of truth, `create_lg_umbrella_fund.py` might need to be verified to ensure it reads from there or `data/onboarding_submissions` correctly.
