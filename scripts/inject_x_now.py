"""
inject_x_now.py — Immediate X.com Injection Runner
===================================================
Reads the UNIFIED_REGISTRY.json and generated pulse videos,
then posts each one to @Upscrolledai with:
  - Campaign title (English)
  - WhyDonate URL  
  - fajr.today brand
  - Gaza/MutualAid hashtags

Run: python scripts/inject_x_now.py [--dry-run]
"""

import os
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

ACTIVE_ROOT   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET_DIR    = os.path.join(ACTIVE_ROOT, 'vault', 'amplification', 'pulse_verticals')
REGISTRY_PATH = os.path.join(ACTIVE_ROOT, 'vault', 'UNIFIED_REGISTRY.json')

# Import the injection function from publish_to_socials
sys.path.insert(0, os.path.join(ACTIVE_ROOT, 'scripts'))
from publish_to_socials import inject_x_posts


def load_campaigns_with_pulses():
    """Match generated pulse .mp4s to their registry campaign metadata using ishmael_id."""
    pulses = []
    if not os.path.exists(TARGET_DIR):
        print(f"Pulse directory not found: {TARGET_DIR}")
        return pulses

    try:
        with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
            registry = json.load(f)
    except Exception as e:
        print(f"Failed to load registry: {e}")
        registry = []

    # Build lookup maps
    by_ishmael = {}  # ishmael_id → campaign
    by_name = {}     # identity_name (lower) → campaign
    for c in registry:
        iid = (c.get('ishmael_id') or '').strip().upper()
        if iid:
            by_ishmael[iid] = c
        identity = (c.get('custom_identity_name') or c.get('identity_name') or '').strip().lower()
        if identity:
            by_name[identity] = c

    mp4_files = sorted([f for f in os.listdir(TARGET_DIR) if f.endswith('.mp4')])
    print(f"Found {len(mp4_files)} pulse files.")

    for fname in mp4_files:
        fpath = os.path.join(TARGET_DIR, fname)
        # Filename format: ISHMAEL_RestOfName_vertical.mp4 or _RestOfName_vertical.mp4
        base = fname.replace('_vertical.mp4', '')

        # Try ishmael_id prefix match first (e.g. "D_Help_Ahmed_D" → "D")
        parts = base.split('_')
        matched = None
        # Single-char prefix = ishmael_id
        if parts[0] and len(parts[0]) <= 2 and parts[0].isupper():
            matched = by_ishmael.get(parts[0])
        
        # Fallback: identity name keyword match
        if not matched:
            base_lower = base.replace('_', ' ').lower()
            for k, c in by_name.items():
                k_words = set(k.split())
                b_words = set(base_lower.split())
                if len(k_words & b_words) >= 2:
                    matched = c
                    break

        wd_url = (matched or {}).get('whydonate_url') or ''
        title  = (matched or {}).get('title') or base.replace('_', ' ')
        iname  = (matched.get('custom_identity_name') or matched.get('identity_name') or '') if matched else base.replace('_',' ')

        pulses.append({
            'video_path':    fpath,
            'filename':      fname,
            'title':         title,
            'identity_name': iname,
            'whydonate_url': wd_url,
        })

    return pulses


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Inject visual pulses to X.com @Upscrolledai")
    parser.add_argument("--dry-run", action="store_true", help="Preview posts without actually posting")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of pulses to process")
    args = parser.parse_args()

    print("🌀 X.com Injection Engine — @Upscrolledai")
    print("=" * 50)
    
    campaign_pulses = load_campaigns_with_pulses()
    if not campaign_pulses:
        print("No pulses found. Run generate_vortex_video.py first.")
        sys.exit(1)
    
    if args.limit:
        print(f"⚠️ Limiting to {args.limit} pulses.")
        campaign_pulses = campaign_pulses[:args.limit]
    
    print(f"\nPreparing to inject {len(campaign_pulses)} pulses:")
    for p in campaign_pulses:
        en_title = p['title'].split('|')[0].strip()[:60] if '|' in p['title'] else p['title'][:60]
        wd = p['whydonate_url'][:40] + '...' if len(p.get('whydonate_url','')) > 40 else p.get('whydonate_url','')
        print(f"  📹 {p['filename'][:40]:40} → {en_title}")
        if wd:
            print(f"       💰 {wd}")

    print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Launching injection...\n")
    
    inject_x_posts(campaign_pulses, check_only=args.dry_run)
    
    print("\n✅ Done.")
