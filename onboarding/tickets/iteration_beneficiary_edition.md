# Modification Ticket: [Iteration 02] Beneficiary Sovereign Edition

**Status**: [DRAFT]
**Priority**: High
**Objective**: Allow 302 beneficiaries to edit their own stories and media without compromising the integrity of the Global Umbrella Fund.

## Background
LaunchGood's native "Team" permissions are coarse: adding a beneficiary as a team member allows them to edit the *entire* campaign story. For 300+ families, this creates a high risk of accidental data loss.

## Proposed Implementation: "Sovereign Edit Sync"

### 1. Portal Enhancement (Local)
- **Feature**: "Update My Story" view in the [Onboarding Portal](file:///c:/Users/gaelf/Documents/GitHub/local_ai_campaign_assistant/onboarding/index.html).
- **Authentication**: Usage of the unique `beneficiary_id` in the URL to load existing draft data from `data/onboarding_submissions`.
- **Validation**: Re-running the **Blood Content Filter** on any new media uploads.

### 2. Synchronization Layer
- **Script**: `scripts/sync_umbrella_edits.py`.
- **Logic**: 
    1. Scan `data/onboarding_submissions` for recent timestamps.
    2. Re-generate the aggregated `story` HTML for the Global Fund.
    3. Use the CDP Automation to update the LaunchGood draft.

## LaunchGood Team Portal Inquiry Result
> [!NOTE]
> **Conclusion**: Native Team Portal access is **unsuitable** for this scale because it lacks section-level granular permissions. Our local portal will act as the "Buffer" for edits, providing a safer and more user-friendly interface for the beneficiaries.

## Success Metrics
- 0% accidental overwrites of other beneficiaries' stories.
- < 5 minute sync time between Portal edit and LaunchGood update.
