import os
import sys
import time
import subprocess
import requests
import json
import re
from datetime import datetime

# Configuration
CONFIG = {
    "work_dir": "c:/Users/gaelf/Documents/GitHub/local_ai_campaign_assistant",
    "server_script": "scripts/onboarding_server.py",
    "tunnel_log": "data/tunnel.log",
    "status_file": "data/status.json",
    "warden_log": "data/warden.log",
    "check_interval": 15,
    "max_tunnel_retries": 5
}

def log(message, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [{level}] {message}"
    print(log_line)
    try:
        with open(CONFIG["warden_log"], "a", encoding="utf-8") as f:
            f.write(log_line + "\n")
    except:
        pass

def get_latest_tunnel_url():
    try:
        if not os.path.exists(CONFIG["tunnel_log"]):
            return None
        with open(CONFIG["tunnel_log"], "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in reversed(lines):
                match = re.search(r"https://[a-z0-9-]+\.trycloudflare\.com", line)
                if match:
                    return match.group(0)
    except Exception as e:
        log(f"Error parsing tunnel log: {e}", "ERROR")
    return None

def update_status(url):
    try:
        status = {
            "last_updated": datetime.now().isoformat() + "Z",
            "services": {
                "onboarding_server": {
                    "status": "online" if url else "offline",
                    "local_url": "http://127.0.0.1:5010",
                    "public_url": url or "OFFLINE"
                },
                "shahada_portal": {
                    "status": "online" if url else "offline",
                    "public_url": f"{url}/onboard" if url else "OFFLINE"
                },
                "brain_portal": {
                    "status": "online" if url else "offline",
                    "public_url": f"{url}/brain" if url else "OFFLINE"
                }
            },
            "meta": {
                "provider": "cloudflare",
                "tunnel_id": "ephemeral-quick-tunnel",
                "failover_active": False,
                "warden_version": "1.0.0"
            }
        }
        with open(CONFIG["status_file"], "w", encoding="utf-8") as f:
            json.dump(status, f, indent=4)
        log(f"Dynamic Resolver updated: {url}")
    except Exception as e:
        log(f"Failed to update status.json: {e}", "ERROR")

def check_local_server():
    try:
        response = requests.get("http://127.0.0.1:5010/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def run_warden():
    log("Warden v1.0 Initializing...")
    tunnel_restarts = 0
    
    while True:
        # 1. Server Check
        if not check_local_server():
            log("Local Onboarding Server is offline. Warden cannot fix process yet (managed externally).", "WARN")
        
        # 2. Tunnel Check & URL Discovery
        current_url = get_latest_tunnel_url()
        
        # Verify public URL health if we have one
        public_healthy = False
        if current_url:
            try:
                # Cloudflare check might fail if tunnel is reconnecting
                res = requests.get(f"{current_url}/health", timeout=5)
                if res.status_code == 200:
                    public_healthy = True
            except:
                pass

        if public_healthy:
            update_status(current_url)
            tunnel_restarts = 0 # Reset cooldown
        else:
            log("Sovereign Tunnel is unhealthy or reconnecting.", "WARN")
            # If the tunnel process is dead, start_stable_tunnel.ps1 should be run
            # For now, Warden monitors and updates. 
            # In Phase 10.2, Warden will OWN the cloudflared process.
        
        time.sleep(CONFIG["check_interval"])

if __name__ == "__main__":
    run_warden()
