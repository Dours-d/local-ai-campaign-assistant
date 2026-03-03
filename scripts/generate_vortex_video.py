import os
import json
import subprocess
import requests
import sys
from urllib.parse import urlparse
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

# ==========================================
# VECTOR 9: THE PULSE (VISUAL RESONANCE)
# ==========================================
# This script extracts the campaign's native image and synthesizes 
# a 15-second vertical video (1080x1920) with a slow algorithmic 
# zoom (Ken Burns) perfectly formatted for up-scrolled platforms
# like TikTok, YouTube Shorts, and Instagram Reels.
#
# NOTE: Audio is intentionally omitted. Algorithmic reach on these
# platforms relies heavily on the user selecting a "trending sound" 
# inside the app prior to posting.
# ==========================================

ACTIVE_ROOT = os.environ.get('ACTIVE_ROOT', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REGISTRY_PATH = os.path.join(ACTIVE_ROOT, 'vault', 'UNIFIED_REGISTRY.json')
OUTPUT_DIR = os.path.join(ACTIVE_ROOT, 'vault', 'amplification', 'pulse_verticals')
TEMP_DIR = os.path.join(ACTIVE_ROOT, 'vault', 'amplification', 'temp')

def download_image(url, ishmael_id):
    """Downloads the campaign image or returns the local path if it's not a URL."""
    if not url.startswith('http'):
        local_path = os.path.join(ACTIVE_ROOT, url)
        if os.path.exists(local_path):
            return local_path
        else:
            print(f"Local image not found: {local_path}")
            return None
            
    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        ext = os.path.splitext(urlparse(url).path)[1]
        if not ext:
            ext = '.jpg'
            
        img_path = os.path.join(TEMP_DIR, f"{ishmael_id}_source{ext}")
        with open(img_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return img_path
    except Exception as e:
        print(f"Failed to download image for {ishmael_id}: {e}")
        return None

def synthesize_vertical_pulse(image_path, title, out_path):
    """Uses FFmpeg to apply a Ken Burns pan and vertical crop."""
    # FFmpeg filter breakdown:
    # 1. scale param maximizes the image while keeping aspect ratio
    # 2. zoompan does a slow center crop zoom lasting exactly 15 seconds (450 frames @ 30fps)
    # 3. crop guarantees a 1080x1920 vertical format for Shorts/TikTok
    
    # Text overlay is kept minimal because the algorithm prefers native
    # text added inside the TikTok/Reels app, but we burn in a small 
    # verification badge/link.
    
    clean_title = title.replace("'", "").replace(":", "")[:40]
    
    # Complex filter for slow zoom + vertical format
    vf_string = (
        "scale=10800:-1,zoompan=z='min(zoom+0.0015,1.5)':d=450:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)',"
        "scale=-1:1920,crop=1080:1920,"
        f"drawtext=text='Mutual Aid Solidarity':fontcolor=white:fontsize=40:x=(w-text_w)/2:y=h-250:box=1:boxcolor=black@0.5:boxborderw=10,"
        f"drawtext=text='{clean_title}':fontcolor=white:fontsize=30:x=(w-text_w)/2:y=h-180:box=1:boxcolor=black@0.5:boxborderw=10"
    )

    cmd = [
        'ffmpeg', '-y', 
        '-loop', '1', 
        '-i', image_path,
        '-vf', vf_string,
        '-c:v', 'libx264', 
        '-t', '15', 
        '-r', '30',
        '-pix_fmt', 'yuv420p',
        out_path
    ]
    
    print("Running FFmpeg... (this takes a few seconds per video)")
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        print(f"FFmpeg failed while processing {image_path}. Check if ffmpeg is installed.")
        return False

def generate_pulse_manifestations():
    print("🌀 Initiating Vector 9 Pulse Synthesizer (Up-scrolled Algorithms)...")
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(TEMP_DIR, exist_ok=True)
        
    try:
        with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
            registry = json.load(f)
    except Exception as e:
        print(f"Failed to load UNIFIED_REGISTRY: {e}")
        return

    # For synthesis, we just need campaigns with valid images. We will relax the whydonate constraint 
    # to ensure the videos can generate even for pending campaigns.
    valid_campaigns = [c for c in registry if c.get('image')]
    
    if not valid_campaigns:
        print("No valid campaigns with images found.")
        return
        
    print(f"Found {len(valid_campaigns)} campaigns ready for visual synthesis.")
    
    # Process all valid campaigns for the mass amplification phase
    for camp in valid_campaigns:
        identity = camp.get('custom_identity_name') or camp.get('identity_name') or camp.get('registry_name') or "Gaza Family"
        ishmael_id = camp.get('ishmael_id', 'X')
        img_url = camp.get('image')
        
        print(f"Synthesizing propagation pulse for: {identity}...")
        
        local_img = download_image(img_url, ishmael_id)
        if not local_img:
            continue
            
        clean_name = "".join([c for c in identity if c.isalpha() or c.isdigit() or c==' ']).rstrip().replace(" ", "_")
        filename = f"{ishmael_id}_{clean_name}_vertical.mp4"
        out_path = os.path.join(OUTPUT_DIR, filename)
        
        success = synthesize_vertical_pulse(local_img, identity, out_path)
        
        if success:
            print(f"✅ Vertical Pulse generated: {out_path}")
            
        # Clean up temp
        if os.path.exists(local_img):
            os.remove(local_img)
            
    print("\nSynthesis complete. 15-second visual pulses are ready for TikTok/Shorts.")
    print("For maximum impact, add trending audio inside the app natively.")

if __name__ == "__main__":
    generate_pulse_manifestations()
