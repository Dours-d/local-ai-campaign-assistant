import os
import json
import re
from datetime import datetime

# ==========================================
# VORTEX NODE GENERATOR (VECTOR 1)
# ==========================================
# This script reads the UNIFIED_REGISTRY and spins out 
# a static, heavily-SEO-optimized .html file for every campaign.
# It strips all metadata linking back to the management repo
# and creates a clean `sitemap.xml` for maximum propagation.
# ==========================================

ACTIVE_ROOT = os.environ.get('ACTIVE_ROOT', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REGISTRY_PATH = os.path.join(ACTIVE_ROOT, 'vault', 'UNIFIED_REGISTRY.json')
OUTPUT_DIR = os.path.join(ACTIVE_ROOT, 'public_nodes')

# Base URL for the disposable outpost (can be changed per deployment)
BASE_URL = "https://palestine-resilience-network.netlify.app"

def clean_filename(name):
    # Strip non-alphanumeric, replace spaces with hyphens
    clean = re.sub(r'[^a-zA-Z0-9\s-]', '', name)
    clean = re.sub(r'[-\s]+', '-', clean).strip('-')
    return clean

def generate_node_html(camp, file_name):
    identity = camp.get('custom_identity_name') or camp.get('identity_name') or camp.get('registry_name') or "Gaza Resilience Fund"
    title = camp.get('title', 'Support our family in Gaza')
    story = camp.get('story') or camp.get('description', 'We are reaching out to secure our family\'s survival and rebuild our lives. Your direct solidarity means everything to us.')
    image_url = camp.get('image_url', '')
    whydonate_url = camp.get('whydonate_url', '#')
    
    # Strip any internal formatting or newlines for meta tags
    meta_desc = story.replace('"', '&quot;').replace('\n', ' ')[:160] + '...'
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{identity} - Mutual Aid & Resilience</title>
    
    <!-- Primary Meta Tags -->
    <meta name="title" content="{identity} - Mutual Aid & Resilience">
    <meta name="description" content="{meta_desc}">
    
    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="website">
    <meta property="og:url" content="{BASE_URL}/{file_name}">
    <meta property="og:title" content="{identity} - Mutual Aid & Resilience">
    <meta property="og:description" content="{meta_desc}">
    {f'<meta property="og:image" content="{image_url}">' if image_url else ''}
    
    <!-- Twitter -->
    <meta property="twitter:card" content="summary_large_image">
    <meta property="twitter:url" content="{BASE_URL}/{file_name}">
    <meta property="twitter:title" content="{identity} - Mutual Aid & Resilience">
    <meta property="twitter:description" content="{meta_desc}">
    {f'<meta property="twitter:image" content="{image_url}">' if image_url else ''}
    
    <style>
        :root {{
            --bg: #0f1115;
            --text: #e2e8f0;
            --primary: #10b981;
            --accent: #059669;
        }}
        body {{
            font-family: system-ui, -apple-system, sans-serif;
            background-color: var(--bg);
            color: var(--text);
            line-height: 1.6;
            margin: 0;
            padding: 0;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            padding: 40px 20px;
        }}
        .card {{
            background: #1e293b;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 20px rgba(0,0,0,0.5);
        }}
        .hero-img {{
            width: 100%;
            height: 400px;
            object-fit: cover;
            border-bottom: 2px solid var(--primary);
        }}
        .content {{
            padding: 30px;
        }}
        h1 {{
            color: #fff;
            margin-top: 0;
            font-size: 2rem;
        }}
        .story {{
            white-space: pre-wrap;
            font-size: 1.1rem;
            color: #cbd5e1;
            margin-bottom: 30px;
        }}
        .donate-btn {{
            display: inline-block;
            background: var(--primary);
            color: #fff;
            text-decoration: none;
            padding: 15px 30px;
            border-radius: 8px;
            font-weight: bold;
            font-size: 1.2rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            transition: background 0.2s;
            text-align: center;
            width: 100%;
            box-sizing: border-box;
        }}
        .donate-btn:hover {{
            background: var(--accent);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            {f'<img src="{image_url}" class="hero-img" alt="{identity}">' if image_url else ''}
            <div class="content">
                <h1>{title}</h1>
                <div class="story">{story}</div>
                <a href="{whydonate_url}" class="donate-btn" target="_blank" rel="noopener noreferrer">Support This Campaign Directly</a>
            </div>
        </div>
    </div>
</body>
</html>
"""
    return html

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    try:
        with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
            registry = json.load(f)
    except Exception as e:
        print(f"Failed to load UNIFIED_REGISTRY: {e}")
        return

    # Filter for campaigns that actually have a whydonate URL or are verified
    valid_campaigns = [c for c in registry if c.get('whydonate_url') or c.get('status') == 'verified' or c.get('status') == 'live']
    
    print(f"Found {len(valid_campaigns)} valid nodes to generate out of {len(registry)} total entries.")
    
    sitemap_urls = []
    
    for camp in valid_campaigns:
        identity = camp.get('custom_identity_name') or camp.get('identity_name') or camp.get('registry_name') or "unknown"
        ishmael_id = camp.get('ishmael_id', 'X')
        
        # Determine unique filename: e.g., Ishmael-A1-Um-Mohammed.html
        base_name = f"{ishmael_id}-{identity}"
        file_name = f"{clean_filename(base_name)}.html"
        
        html_content = generate_node_html(camp, file_name)
        
        out_path = os.path.join(OUTPUT_DIR, file_name)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        sitemap_urls.append(f"{BASE_URL}/{file_name}")
        
    # Generate Sitemap
    sitemap_path = os.path.join(OUTPUT_DIR, 'sitemap.xml')
    today = datetime.now().strftime('%Y-%m-%d')
    sitemap_content = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for url in sitemap_urls:
        sitemap_content += f"  <url>\n    <loc>{url}</loc>\n    <lastmod>{today}</lastmod>\n    <changefreq>weekly</changefreq>\n  </url>\n"
    sitemap_content += "</urlset>"
    
    with open(sitemap_path, 'w', encoding='utf-8') as f:
        f.write(sitemap_content)
        
    print(f"Successfully generated {len(sitemap_urls)} node files in {OUTPUT_DIR}")
    print(f"Generated complete sitemap.xml")

if __name__ == "__main__":
    main()
