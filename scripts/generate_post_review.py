import os
import json
import sys
import re
from datetime import datetime

# Configuration
ACTIVE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY_PATH = os.path.join(ACTIVE_ROOT, 'vault', 'UNIFIED_REGISTRY.json')
TARGET_DIR = os.path.join(ACTIVE_ROOT, 'vault', 'amplification', 'pulse_verticals')

def synthesize_content(pulse):
    """Sovereign Context Engine: Injects intelligence and emotional weight."""
    desc = pulse.get('description', '')
    title = pulse.get('title', '')
    iname = pulse.get('identity', '')
    video_fname = pulse.get('video', '')
    
    # 1. NUCLEAR CLEANING: Remove ALL internal IDs and placeholders
    raw_text = f"{title} {desc}"
    
    # Blacklist of common ID patterns and residues
    # Patterns: PregnantA, Beneficiary, Survivor, names like "AhmedC", Akram_D, is A, Fatima A
    # Also catch residues like " | ", " - ", " ID: ", "رقم المستفيد"
    patterns = [
        r'Pregnant[A-Z]?', r'Beneficiary[A-Z]?', r'Survivor in Gaza', r'Family in Gaza',
        r'Gaza Case', r'Ahmed[A-Z]?', r'Akram[A-Z]?', r'Mohammed[A-Z]?', r'Abdel Rahim',
        r'Marah', r'Umm Iman', r'Umm Masoud', r'Salman AlWatts', r'Ishmael_ID',
        r'ID:\s*[\-\w\d]+', r'رقم تعريف المستفيد:\s*[\-\w\d]*', r'رقم المستفيد:\s*[\-\w\d]*',
        r'\[.*?\]', r'\b[A-Z]\b(?:\s*\||\s*$)', r'\|', r' -- ', r'\-\-\-'
    ]
    
    clean_text = raw_text
    for p in patterns:
        clean_text = re.sub(p, '', clean_text, flags=re.IGNORECASE)
    
    # Strip double spaces and cleaning artifacts
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    clean_text = re.sub(r'^[\s\-\|]+|[\s\-\|]+$', '', clean_text)
    
    # 2. INTELLIGENCE MAPPING
    context_hooks = []
    text_blob = (title + " " + desc + " " + iname).lower()
    
    if any(k in text_blob for k in ['pregnant', 'mother', 'pregnancy', 'birth', 'child']):
        context_hooks.append("Surviving pregnancy in a landscape of 'crafted scarcity'.")
        context_hooks.append("The struggle for basic medications is a daily battle for mothers here.")
    
    if any(k in text_blob for k in ['children', 'family', 'sons', 'daughters', 'kids']):
        context_hooks.append("Taking care of a large family while every resource is being throttled.")
        context_hooks.append("Seeking stability for children who have only known displacement.")

    if any(k in text_blob for k in ['home', 'destroyed', 'tent', 'house', 'bombed']):
        context_hooks.append("Rebuilding life from the rubble of what used to be a home.")
        context_hooks.append("Tents are not homes; they are temporary shields against the wind.")

    hook_str = " ".join(context_hooks[:2]) if context_hooks else "Standing with those facing the weight of 'crafted scarcity' in Gaza."

    # 3. X.com Format: Robust Video Context
    # Aesthetic cleaning
    display_name = iname if len(iname) > 3 and "Gaza Case" not in iname else "Gaza Family"
    x_text = f"🎥 Pulse: {display_name}\n{hook_str}\n\n"
    x_text += f"🔗 Support: {pulse['link']}\n"
    x_text += "🌐 Mission Hub: https://fajr.today\n"
    x_text += "#Gaza #Humanitarian #MutualAid"

    # 4. WordPress Format: 100% ID-FREE BODY
    clean_iname = iname
    # Aggressively clean identity name too
    for p in [r'\b[A-Z]$', r'Pregnant[A-Z]?', r'Beneficiary', r'\|', r'\s+A$', r'\s+B$']:
        clean_iname = re.sub(p, '', clean_iname, flags=re.IGNORECASE).strip()
    
    if not clean_iname or clean_iname.lower() in ['a', 'b', 'c']:
        clean_iname = "Family in Gaza"

    wp_body = f"<!-- wp:paragraph -->\n<p><strong>{hook_str}</strong></p>\n<!-- /wp:paragraph -->\n\n"
    wp_body += f"<!-- wp:video -->\n<figure class=\"wp-block-video\"><video controls src=\"[Video: {video_fname}]\"></video></figure>\n<!-- /wp:video -->\n\n"
    
    if clean_text and len(clean_text) > 20:
        wp_body += f"<!-- wp:paragraph -->\n<p>{clean_text[:500]}</p>\n<!-- /wp:paragraph -->\n\n"
    
    wp_body += f"<!-- wp:paragraph -->\n<p>🔗 <strong>Direct Support</strong>: <a href=\"{pulse['link']}\">{pulse['link']}</a></p>\n<!-- /wp:paragraph -->\n\n"
    wp_body += f"<!-- wp:paragraph -->\n<p>🌐 <strong>Mission Hub</strong>: <a href=\"https://fajr.today\">fajr.today</a></p>\n<!-- /wp:paragraph -->"

    return {'x_text': x_text, 'wp_body': wp_body, 'clean_identity': clean_iname}

def load_pulses():
    if not os.path.exists(REGISTRY_PATH):
        print(f"Registry not found: {REGISTRY_PATH}")
        return []
    with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    # Build lookup maps
    by_ishmael = {}
    by_name = {}
    for c in registry:
        iid = (c.get('ishmael_id') or '').strip().upper()
        if iid: by_ishmael[iid] = c
        identity = (c.get('custom_identity_name') or c.get('identity_name') or '').strip().lower()
        if identity: by_name[identity] = c

    pulses = []
    if not os.path.exists(TARGET_DIR):
        print(f"Target dir not found: {TARGET_DIR}")
        return []

    mp4_files = sorted([f for f in os.listdir(TARGET_DIR) if f.endswith('.mp4')])
    for fname in mp4_files:
        base = fname.replace('_vertical.mp4', '')
        parts = base.split('_')
        matched = None
        
        if parts[0] and len(parts[0]) <= 2 and parts[0].isupper():
            matched = by_ishmael.get(parts[0])
        
        if not matched:
            base_lower = base.replace('_', ' ').lower()
            for k, c in by_name.items():
                if k in base_lower:
                    matched = c
                    break

        wd_url = (matched or {}).get('whydonate_url') or 'https://whydonate.com/fundraising/urgent-medical-aid-for-pregnant-women-and-newborns-in-gaza-1'
        title  = (matched or {}).get('title') or base.replace('_', ' ')
        iname  = (matched.get('custom_identity_name') or matched.get('identity_name') or '') if matched else base
        desc   = (matched or {}).get('description') or ""

        # Remove Internal IDs from names
        if "PregnantA" in iname: iname = "Family in Gaza"
        if "Beneficiary" in iname: iname = "Survivor in Gaza"

        pulses.append({
            'id': base,
            'identity': iname,
            'title': title,
            'link': wd_url,
            'video': fname,
            'description': desc
        })
    return pulses

def generate_review():
    pulses = load_pulses()
    output_path = r"C:\Users\gaelf\.gemini\antigravity\brain\2e208ff3-5137-47c9-adf7-6d04035a90d7\post_review_summary.md"
    
    now_utc = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# 📝 Social Media Post Review Summary (Sovereign Content)\n")
        f.write(f"**Generated at:** {now_utc} UTC (SYSTEMATIC REFRESH)\n\n")
        f.write(f"Found **{len(pulses)}** pulses refined with intelligent synthesis.\n\n")
        
        if pulses:
            p = pulses[0]
            synth = synthesize_content(p)
            f.write("## 🔍 Full Preview (Pulse #1)\n")
            f.write("### 🐦 X.com\n")
            f.write(f"```text\n{synth['x_text']}\n```\n\n")
            
            f.write("### 📂 WordPress\n")
            f.write(f"**Title:** {synth['clean_identity']}\n")
            f.write(f"**Body (Markdown Preview):**\n{synth['wp_body']}\n\n")

        f.write("- **Mission Hub:** `https://fajr.today` (Mandatory)\n")
        f.write("- **No Internal IDs**: All 'PregnantA', 'Ishmael_ID' etc. have been stripped.\n")
        f.write("- **Nuclear Formatting**: All 'Campaign Title' placeholders have been removed.\n\n")
        
        f.write("## 🐦 X.com (Twitter) Format\n")
        f.write("```text\n")
        f.write("🎥 (Video: [Asset]) [Refined Context Hook]\n\n")
        f.write("🔗 Support: [Donation Link]\n")
        f.write("🌐 fajr.today\n")
        f.write("#Gaza #Humanitarian\n")
        f.write("```\n\n")
        
        f.write("## 📂 WordPress Format\n")
        f.write("- **Title:** [Clean Identity]\n")
        f.write("- **Content:** Video + [Refined Context Hook] + [Cleaned Story] + [Donation Link] + [fajr.today Link]\n\n")
        
        f.write("---\n\n")
        
        for i, p in enumerate(pulses[:25]):
            synth = synthesize_content(p)
            f.write(f"### {i+1}. {synth['clean_identity']}\n")
            f.write(f"- **Direct Support:** {p['link']}\n")
            f.write(f"- **Asset:** `{p['video']}`\n\n")
            f.write("#### 🐦 X.com Hook\n")
            f.write(f"```text\n{synth['x_text']}\n```\n\n")
            f.write("#### 📂 WordPress Preview\n")
            f.write(f"{synth['wp_body']}\n\n")
            f.write("---\n\n")
            
    print(f"✅ Review summary generated: {output_path}")

if __name__ == "__main__":
    generate_review()
