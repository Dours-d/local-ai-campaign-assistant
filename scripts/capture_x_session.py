import os
import sys
import time
from playwright.sync_api import sync_playwright

# This script allows a manual login to X.com to capture the storage state (cookies/local-storage)
# to bypass anti-bot login triggers in automated scripts.

ACTIVE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUTH_STATE_PATH = os.path.join(ACTIVE_ROOT, 'scripts', 'data', 'x_auth_state.json')

def capture_session():
    print("🌀 Initiating Manual Session Bridge for X.com...")
    print("⚠️  A browser window will open. Please log in manually.")
    print(f"⚠️  Once logged in and at the home feed, return here and press Enter.")
    
    if not os.path.exists(os.path.dirname(AUTH_STATE_PATH)):
        os.makedirs(os.path.dirname(AUTH_STATE_PATH), exist_ok=True)

    with sync_playwright() as p:
        # Launch headed browser for manual interaction
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        page.goto("https://x.com/login")
        
        input("\n[Action Required] Log in to X.com and press Enter here when ready to save session...")
        
        # Save storage state
        context.storage_state(path=AUTH_STATE_PATH)
        print(f"✅ Session state saved to: {AUTH_STATE_PATH}")
        
        browser.close()

if __name__ == "__main__":
    capture_session()
