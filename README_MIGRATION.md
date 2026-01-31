# Campaign Data Preparation

To run the gap analysis, we need two JSON files in the `data/` directory.

## 1. data/chuffed_campaigns.json
This file should contain the list of all campaigns from Chuffed.
**Format:**
```json
[
  {
    "title": "Campaign Title A",
    "url": "https://chuffed.org/project/a",
    "raised": 1200
  },
  {
    "title": "Campaign Title B",
    "url": "https://chuffed.org/project/b",
    "raised": 500
  }
]
```

## 2. data/whydonate_campaigns.json
This file should contain the list of all campaigns currently on Whydonate.
**Format:**
```json
[
  {
    "title": "Campaign Title A",
    "url": "https://whydonate.nl/fundraising/a"
  }
]
```

## How to get this data?
If you don't have these files, we can generate them by:
1.  **Whydonate**: Visiting the profile page and copying the campaign titles/links (or using a script).
2.  **Chuffed**: Using the provided credentials to export data, or scraping the profile page.

## Running the Analysis
Once files are ready:
```bash
node scripts/analyze_campaign_gap.js
```
This will generate `data/migration_todo.json`.
