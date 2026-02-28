import os
import json
import random
from datetime import datetime

# ==========================================
# VECTOR 6: NETWORK-READY CONTENT FORGE
# ==========================================
# This script curates a "Weekly Resilience Bulletin" from the
# unified registry. It formats 3-5 urgent campaigns into a 
# clean, highly-readable block of text designed specifically 
# for WhatsApp, Telegram, or Matrix propagation.
# ==========================================

ACTIVE_ROOT = os.environ.get('ACTIVE_ROOT', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REGISTRY_PATH = os.path.join(ACTIVE_ROOT, 'data', 'UNIFIED_REGISTRY.json')
OUTPUT_DIR = os.path.join(ACTIVE_ROOT, 'vault', 'amplification')

# Optional: Link to the decentralized SEO node if preferred over WhyDonate
# SEO_OUTPOST_URL = "https://palestine-resilience-network.netlify.app"

def clean_story_preview(story):
    if not story:
        return "Rebuilding our lives and securing our family's future."
    # Take the first coherent sentence or up to 100 characters
    preview = story.split('.')[0].strip()
    if len(preview) < 20 and '.' in story[len(preview)+1:]:
        preview += '. ' + story[len(preview)+1:].split('.')[0].strip()
    
    if len(preview) > 120:
        preview = preview[:117] + "..."
    else:
        preview += "."
    return preview

def generate_digest():
    print("🌀 Forging Network-Ready Digest (Vector 6)...")
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    try:
        with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
            registry = json.load(f)
    except Exception as e:
        print(f"Failed to load UNIFIED_REGISTRY: {e}")
        return

    # Filter for active campaigns with links
    valid_campaigns = [c for c in registry if c.get('whydonate_url') and c.get('status') in ['live', 'verified']]
    
    if len(valid_campaigns) == 0:
        print("No live campaigns found to forge a digest. Ensure campaigns are marked 'live' or 'verified' and have a Whydonate URL.")
        return
        
    # Select up to 5 campaigns
    selected = random.sample(valid_campaigns, min(5, len(valid_campaigns)))
    
    date_str = datetime.now().strftime('%B %d, %Y')
    
    # WhatsApp/Telegram formatting uses * for bold and _ for italics
    digest_lines = [
        f"🌱 *Sovereign Resilience Bulletin | {date_str}* 🌱\n",
        "Direct mutual aid to families in Gaza. No middleman. No overhead. Just human-to-human solidarity.\n",
        "Here are families waiting for a lifeline today:\n"
    ]
    
    for _, camp in enumerate(selected, 1):
        name = camp.get('custom_identity_name') or camp.get('identity_name') or camp.get('registry_name') or "Gaza Family"
        url = camp.get('whydonate_url')
        story = camp.get('story') or camp.get('description', '')
        preview = clean_story_preview(story)
        
        digest_lines.append(f"🔹 *{name}*")
        digest_lines.append(f"_{preview}_")
        digest_lines.append(f"🔗 {url}\n")
        
    digest_lines.append("────────────────")
    digest_lines.append("100% of funds go directly to the families' managed wallets. Please forward this to your networks to multiply the resonance.")

    digest_text = "\n".join(digest_lines)
    
    filename = f"digest_v6_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    out_path = os.path.join(OUTPUT_DIR, filename)
    
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(digest_text)
        
    print(f"\n✅ DIGEST FORGED: {out_path}")
    print("\n--- PREVIEW ---")
    print(digest_text)
    print("-----------------\n")
    print("The human network can now copy and paste this into their transmission channels.")

if __name__ == "__main__":
    generate_digest()
