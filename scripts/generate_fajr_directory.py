import json
import os
import datetime
import shutil

ACTIVE_ROOT = os.environ.get('ACTIVE_ROOT', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REGISTRY_PATH = os.path.join(ACTIVE_ROOT, 'vault', 'UNIFIED_REGISTRY.json')
OUTPUT_DIR = os.path.join(ACTIVE_ROOT, 'vault', 'amplification')
MEDIA_OUTPUT_DIR = os.path.join(OUTPUT_DIR, 'media')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'index.html')

# New Frontend Sync Paths
FRONTEND_DIR = os.path.join(ACTIVE_ROOT, 'frontend')
FRONTEND_ASSETS_DIR = os.path.abspath(os.path.join(FRONTEND_DIR, 'assets', 'campaigns'))
FRONTEND_DATA_FILE = os.path.abspath(os.path.join(FRONTEND_DIR, 'data', 'registry.json'))



def generate_fajr_directory():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(MEDIA_OUTPUT_DIR, exist_ok=True)
    os.makedirs(FRONTEND_ASSETS_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(FRONTEND_DATA_FILE), exist_ok=True)

    
    if not os.path.exists(REGISTRY_PATH):
        print(f"ERROR: Cannot find {REGISTRY_PATH}")
        return

    with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
        registry = json.load(f)

    # Filter to valid campaigns that have a Whydonate URL and aren't discarded
    valid_campaigns = [
        c for c in registry
        if isinstance(c, dict) and c.get('whydonate_url') and c.get('whydonate_url') != "" and c.get('status', '').upper() != 'DISCARDED'
    ]
    
    # Sort campaigns to put highest priority or newest first
    valid_campaigns.sort(key=lambda x: str(x.get('ishmael_id') or 'Z'))

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sovereign Trust | Active Campaigns</title>
    <!-- Modern typography -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Inter:wght@400;600&display=swap" rel="stylesheet">
    
    <style>
        :root {{
            --bg-color: #0F172A; /* Slate 900 */
            --surface-color: #1E293B; /* Slate 800 */
            --accent-color: #38BDF8; /* Light blue accent */
            --text-main: #F8FAFC;
            --text-muted: #94A3B8;
            --border-color: rgba(255, 255, 255, 0.1);
        }}
        
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        
        body {{
            background-color: var(--bg-color);
            color: var(--text-main);
            font-family: 'Inter', sans-serif;
            line-height: 1.6;
            -webkit-font-smoothing: antialiased;
        }}
        
        header {{
            text-align: center;
            padding: 4rem 2rem 2rem;
            border-bottom: 1px solid var(--border-color);
            background: linear-gradient(180deg, rgba(15,23,42,1) 0%, rgba(30,41,59,0.5) 100%);
        }}
        
        h1 {{
            font-family: 'Outfit', sans-serif;
            font-size: 3rem;
            font-weight: 800;
            letter-spacing: -1px;
            margin-bottom: 1rem;
            background: linear-gradient(90deg, #F8FAFC 0%, #94A3B8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        .header-subtitle {{
            color: var(--text-muted);
            font-size: 1.1rem;
            max-width: 600px;
            margin: 0 auto;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 3rem 2rem;
        }}

        .campaign-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 2rem;
        }}

        .card {{
            background: var(--surface-color);
            border-radius: 16px;
            overflow: hidden;
            border: 1px solid var(--border-color);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            display: flex;
            flex-direction: column;
        }}

        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.5);
            border-color: rgba(56, 189, 248, 0.3);
        }}

        .card-image {{
            width: 100%;
            height: 220px;
            object-fit: cover;
            border-bottom: 1px solid var(--border-color);
        }}
        
        /* Fallback gradient if no image is present */
        .card-image-fallback {{
            width: 100%;
            height: 220px;
            background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            border-bottom: 1px solid var(--border-color);
            color: var(--text-muted);
            font-family: 'Outfit', sans-serif;
            font-size: 2rem;
            font-weight: 800;
            opacity: 0.5;
        }}

        .card-content {{
            padding: 1.5rem;
            flex-grow: 1;
            display: flex;
            flex-direction: column;
        }}

        .card-id {{
            font-family: 'Outfit', sans-serif;
            font-size: 0.85rem;
            font-weight: 800;
            color: var(--accent-color);
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 0.5rem;
        }}

        .card-title {{
            font-family: 'Outfit', sans-serif;
            font-size: 1.4rem;
            font-weight: 600;
            margin-bottom: 1rem;
            line-height: 1.3;
        }}

        .card-story {{
            color: var(--text-muted);
            font-size: 0.95rem;
            margin-bottom: 1.5rem;
            flex-grow: 1;
            display: -webkit-box;
            -webkit-line-clamp: 4;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}

        .card-actions {{
            display: flex;
            gap: 1rem;
            margin-top: auto;
        }}

        .btn {{
            flex: 1;
            padding: 0.8rem;
            text-align: center;
            border-radius: 8px;
            font-weight: 600;
            text-decoration: none;
            transition: all 0.2s ease;
            font-size: 0.95rem;
        }}

        .btn-support {{
            background: var(--text-main);
            color: var(--bg-color);
            border: 1px solid var(--text-main);
        }}

        .btn-support:hover {{
            background: var(--accent-color);
            border-color: var(--accent-color);
            box-shadow: 0 0 15px rgba(56, 189, 248, 0.4);
        }}

        .btn-spread {{
            background: transparent;
            color: var(--text-main);
            border: 1px solid var(--border-color);
        }}

        .btn-spread:hover {{
            background: rgba(255,255,255,0.05);
            border-color: var(--text-muted);
        }}

        footer {{
            text-align: center;
            padding: 3rem 2rem;
            color: var(--text-muted);
            font-size: 0.9rem;
            border-top: 1px solid var(--border-color);
            margin-top: 4rem;
        }}
    </style>
</head>
<body>
    <header>
        <h1>Sovereign Preservers</h1>
        <p class="header-subtitle">Execute your Amanah. Direct, peer-to-peer preservation devoid of centralized friction. These are the ground truths verified by the Sovereign Trust.</p>
    </header>

    <div class="container">
        <div class="campaign-grid">
"""

    for camp in valid_campaigns:
        # Prioritize 'custom_identity_name' or 'title' (for fixed real-world injection)
        identity = camp.get('custom_identity_name') or camp.get('title') or camp.get('identity_name') or camp.get('registry_name') or "Unknown Identity"
        ishmael_id = camp.get('ishmael_id', '???')
        story = camp.get('story') or camp.get('description') or "No presentation available."
        
        if len(story) > 180:
            story = story[:177] + "..."
            
        url = camp.get('whydonate_url', '#')
        
        # Asset Management: Copy images to local media/ folder for deployment
        img_src = camp.get('image', '')
        final_img_url = ""
        
        if img_src:
            abs_img_src = os.path.join(ACTIVE_ROOT, img_src)
            img_filename = os.path.basename(img_src)
            abs_img_dst = os.path.join(MEDIA_OUTPUT_DIR, img_filename)
            
            if os.path.exists(abs_img_src):
                shutil.copy2(abs_img_src, abs_img_dst)
                final_img_url = f"media/{img_filename}"
            else:
                print(f"WARNING: Image not found: {abs_img_src}")

        if final_img_url:
            img_html = f'<img src="{final_img_url}" alt="{identity}" class="card-image">'
        else:
            img_html = f'<div class="card-image-fallback">{ishmael_id}</div>'
            
        encoded_url = url.replace(":", "%3A").replace("/", "%2F")
        spread_link = f"https://twitter.com/intent/tweet?text=Support%20the%20{identity.replace(' ', '%20')}:&url={encoded_url}"

        html_content += f"""
            <div class="card">
                {img_html}
                <div class="card-content">
                    <div class="card-id">ID: {ishmael_id}</div>
                    <div class="card-title">{identity}</div>
                    <div class="card-story">{story}</div>
                    <div class="card-actions">
                        <a href="{url}" target="_blank" class="btn btn-support">Support</a>
                        <a href="{spread_link}" target="_blank" class="btn btn-spread">Spread</a>
                    </div>
                </div>
            </div>
"""

    html_content += f"""
        </div>
    </div>
    
    <footer>
        <p>Generated by the Nuclear Referencing Plant • {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </footer>
</body>
</html>
"""

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✅ Generated Master Directory Page: {OUTPUT_FILE}")
    print(f"   Indexed {len(valid_campaigns)} campaigns.")

    # Export to Frontend Registry
    with open(FRONTEND_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(valid_campaigns, f, indent=2, ensure_ascii=False)
    print(f"✅ Exported Frontend Registry: {FRONTEND_DATA_FILE}")

    # Copy images to frontend assets
    print(f"Syncing assets to: {FRONTEND_ASSETS_DIR}")
    os.makedirs(FRONTEND_ASSETS_DIR, exist_ok=True)
    
    # Potential base directories for recursive search
    base_search_dirs = [
        os.path.abspath(os.path.join(ACTIVE_ROOT, 'vault')),
        os.path.abspath(os.path.join(ACTIVE_ROOT, 'data')),
    ]
    
    for camp in valid_campaigns:
        raw_img_src = camp.get('image', '')
        img_src = raw_img_src.strip()
        if not img_src:
            continue
            
        abs_img_src = os.path.abspath(img_src)
        img_filename = os.path.basename(abs_img_src)
        abs_img_dst = os.path.join(FRONTEND_ASSETS_DIR, img_filename)
        
        found_path = None
        if os.path.exists(abs_img_src):
            found_path = abs_img_src
        else:
            # Recursive search in base directories
            for bdir in base_search_dirs:
                for root, dirs, files in os.walk(bdir):
                    if img_filename in files:
                        found_path = os.path.join(root, img_filename)
                        break
                if found_path:
                    break
        
        if found_path:
            # print(f"  COPYING: {found_path} -> {abs_img_dst}")
            shutil.copy2(found_path, abs_img_dst)
        else:
            print(f"  MISSING: {img_filename} (searched all data/vault)")






if __name__ == "__main__":
    generate_fajr_directory()
