import json
import sys
import io

# Configure UTF-8 encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Load all campaigns
with open('data/campaigns_automation_format.json', 'r', encoding='utf-8') as f:
    all_campaigns = json.load(f)

print(f"Total campaigns: {len(all_campaigns)}")

# Read batch log to find completed campaigns
completed_bids = set()
try:
    with open('data/batch_run_v5_all_166.log', 'r', encoding='utf-8') as f:
        for line in f:
            if 'Processing Step 1' in line:
                # Extract bid from screenshot filename
                if 'verify_s1_' in line:
                    parts = line.split('verify_s1_')[1].split('.png')[0]
                    completed_bids.add(parts)
except FileNotFoundError:
    print("No log file found - will process all campaigns")

print(f"Completed campaigns: {len(completed_bids)}")

# Filter remaining campaigns
remaining = [c for c in all_campaigns if c['bid'] not in completed_bids]

print(f"Remaining campaigns: {len(remaining)}")

# Save remaining campaigns
with open('data/campaigns_remaining.json', 'w', encoding='utf-8') as f:
    json.dump(remaining, f, ensure_ascii=False, indent=2)

print(f"\n✅ Saved {len(remaining)} remaining campaigns to data/campaigns_remaining.json")
print(f"✅ Ready to resume tomorrow!")
