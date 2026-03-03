import os
import json
import datetime
import logging
import urllib.request

# Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PULSE_DIR = os.path.join(BASE_DIR, 'frontend', 'assets', 'pulses')
MANIFEST_PATH = os.path.join(PULSE_DIR, 'manifest.json')
INTEGRITY_SUMMARY = os.path.join(BASE_DIR, 'data', 'integrity_summary.json')
LOG_FILE = os.path.join(BASE_DIR, 'data', 'integrity_checks.log')

# Critical Service Endpoints
SHAHADA_TUNNEL_URL = "https://local-ai-onboarding-portal.loca.lt"

# Simplified Configuration: Core Pulse Assets
CRITICAL_ASSETS = [
    os.path.join('frontend', 'index.html'),
    os.path.join('frontend', 'trustee_dashboard.html'),
    os.path.join('frontend', 'images', 'logo-transparency-enhanced2.png'),
    os.path.join('frontend', 'images', 'Fajr-enhanced.jpeg'),
    os.path.join('frontend', 'images', 'Shahada.png')
]

# Initialize Logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("VisualIntegrity")

def verify_assets():
    """Checks the local manifest, verifies file existence, and validates service tunnels."""
    results = {
        "status": "healthy",
        "last_check": datetime.datetime.now().isoformat(),
        "total_pulses": 0,
        "missing_files": [],
        "critical_failures": [],
        "corrupt_manifest": False,
        "sync_status": "synced",
        "service_status": {}
    }

    logger.info("--- Starting Visual Integrity Check ---")

    # 1. Check Critical Assets (Simplified Config)
    for asset_rel in CRITICAL_ASSETS:
        abs_path = os.path.join(BASE_DIR, asset_rel)
        if not os.path.exists(abs_path):
            results["critical_failures"].append(asset_rel)
            results["status"] = "error"
            logger.error(f"CRITICAL ASSET MISSING: {asset_rel}")
        else:
            logger.info(f"Verified critical asset: {asset_rel}")

    # 2. Check Shahada Tunnel Health
    logger.info(f"Checking Shahada Tunnel: {SHAHADA_TUNNEL_URL}")
    try:
        req = urllib.request.Request(SHAHADA_TUNNEL_URL, method='HEAD')
        req.add_header("bypass-tunnel-reminder", "1")
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                results["service_status"]["shahada_tunnel"] = "healthy"
                logger.info("Shahada Tunnel is ONLINE.")
            else:
                results["service_status"]["shahada_tunnel"] = f"unhealthy ({response.status})"
                results["status"] = "degraded"
                logger.warning(f"Shahada Tunnel returned status: {response.status}")
    except Exception as e:
        results["service_status"]["shahada_tunnel"] = f"offline ({str(e)})"
        results["critical_failures"].append("shahada_tunnel_offline")
        results["status"] = "error"
        logger.error(f"Shahada Tunnel is OFFLINE: {str(e)}")

    # 3. Check Pulse Manifest
    if not os.path.exists(MANIFEST_PATH):
        logger.warning(f"Manifest missing at {MANIFEST_PATH}")
        if results["status"] == "healthy":
            results["status"] = "degraded"
        results["status_message"] = "Pulse manifest missing"
    else:
        try:
            with open(MANIFEST_PATH, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
                results["total_pulses"] = len(manifest)
                logger.info(f"Checking {results['total_pulses']} pulses from manifest.")
                
                for item in manifest:
                    file_path = os.path.join(BASE_DIR, 'frontend', item['url'].lstrip('/'))
                    if not os.path.exists(file_path):
                        results["missing_files"].append(item['filename'])
                        if results["status"] != "error":
                            results["status"] = "degraded"
                        logger.warning(f"Pulse asset missing: {item['filename']} at {file_path}")
                    
        except Exception as e:
            results["status"] = "error"
            results["corrupt_manifest"] = True
            results["status_message"] = f"Manifest corruption: {str(e)}"
            logger.error(f"Manifest error: {str(e)}")

    # 4. Check for Broken Image References in Frontend HTML
    html_files = [os.path.join(BASE_DIR, 'frontend', 'index.html'), os.path.join(BASE_DIR, 'frontend', 'campaigns.html')]
    for html_file in html_files:
        if os.path.exists(html_file):
            logger.info(f"Scanning {os.path.basename(html_file)} for broken images...")
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    import re
                    # Match <img src="..."> tags
                    img_matches = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', content)
                    for img_src in img_matches:
                        # Resolve relative path
                        if img_src.startswith('http'):
                            continue # Skip external for now or use HEAD
                        
                        # Handle relative paths based on HTML location
                        rel_img = img_src.lstrip('./').replace('/', os.sep)
                        if '..' in img_src:
                            # Simple parent dir resolution
                            abs_img = os.path.abspath(os.path.join(os.path.dirname(html_file), img_src.replace('/', os.sep)))
                        else:
                            abs_img = os.path.join(os.path.dirname(html_file), rel_img)

                        if not os.path.exists(abs_img) or os.path.getsize(abs_img) == 0:
                            results["missing_files"].append(f"{os.path.basename(html_file)} -> {img_src}")
                            if results["status"] != "error":
                                results["status"] = "degraded"
                            logger.warning(f"BROKEN IMAGE in {os.path.basename(html_file)}: {img_src}")
                        else:
                            logger.info(f"Image verified: {img_src}")
            except Exception as e:
                logger.error(f"Error scanning {html_file}: {str(e)}")

    if results["critical_failures"]:
        results["status_message"] = f"CRITICAL FAILURE: {len(results['critical_failures'])} issues detected."
    elif results["missing_files"]:
        results["status_message"] = f"Degraded: {len(results['missing_files'])} assets missing/broken."
    elif not results.get("status_message"):
        results["status_message"] = "All systems nominal."

    logger.info(f"Final Status: {results['status']} - {results['status_message']}")
    return results

def save_integrity(results):
    os.makedirs(os.path.dirname(INTEGRITY_SUMMARY), exist_ok=True)
    with open(INTEGRITY_SUMMARY, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print(f"Integrity status: {results['status']} - Saved to {INTEGRITY_SUMMARY}")

if __name__ == "__main__":
    print("🔍 Running Visual Integrity & Sync Check...")
    status = verify_assets()
    save_integrity(status)
