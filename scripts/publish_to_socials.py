import os
import sys
import time
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')

ACTIVE_ROOT = os.environ.get('ACTIVE_ROOT', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENV_PATH = os.path.join(ACTIVE_ROOT, '.env.social')
AUTH_STATE_PATH = os.path.join(ACTIVE_ROOT, 'scripts', 'data', 'x_auth_state.json')
load_dotenv(os.path.join(ACTIVE_ROOT, '.env')) # Load primary Admin keys
load_dotenv(ENV_PATH) # Load social specific keys

TARGET_DIR = os.path.join(ACTIVE_ROOT, 'vault', 'amplification', 'pulse_verticals')

# Platform Credentials
SOCIAL_X_EMAIL = os.environ.get('SOCIAL_X_EMAIL')
SOCIAL_X_PASS = os.environ.get('SOCIAL_X_PASS')
SOCIAL_LINKEDIN_USER = os.environ.get('SOCIAL_LINKEDIN_USER')
SOCIAL_LINKEDIN_PASS = os.environ.get('SOCIAL_LINKEDIN_PASS')
SOCIAL_MASTODON_USER = os.environ.get('SOCIAL_MASTODON_USER')
SOCIAL_MASTODON_PASS = os.environ.get('SOCIAL_MASTODON_PASS')

# fajr.today Portal (Admin)
FAJR_TODAY_ADMIN_USER = os.environ.get('ADMIN_EMAIL') 
FAJR_TODAY_ADMIN_PASS = os.environ.get('ADMIN_PASSWORD')
FAJR_TODAY_URL = os.environ.get('FAJR_TODAY_URL', 'http://127.0.0.1:5010')

def verify_login(platform, page):
    """Verifies if login was successful based on URL or elements."""
    print(f"Verifying {platform} session...")
    if platform == "X":
        try:
            page.wait_for_selector('[data-testid="SideNav_NewTweet_Button"]', timeout=10000)
            return True
        except:
            return False
    elif platform == "LinkedIn":
        try:
            page.wait_for_selector('.global-nav', timeout=10000)
            return True
        except:
            return False
    elif platform == "Mastodon":
        try:
            page.wait_for_selector('.compose-form__textarea', timeout=10000)
            return True
        except:
            return False
    return False

def check_x(page):
    try:
        # Check if we have an auth state to bypass login
        if os.path.exists(AUTH_STATE_PATH):
            print("🔄 Using persistent session for X.com...")
            page.goto("https://x.com/home", wait_until="networkidle")
            if verify_login("X", page):
                return True
            print("⚠️ Persistent session expired or invalid. Attempting cold login...")

        print(f"Navigating to X/Twitter... (User: {SOCIAL_X_EMAIL})")
        page.goto("https://x.com/login", wait_until="networkidle")
        
        # User field
        page.wait_for_selector('input[autocomplete="username"]', timeout=15000)
        page.type('input[autocomplete="username"]', SOCIAL_X_EMAIL, delay=100)
        page.keyboard.press("Enter")
        time.sleep(5)
        
        # Identity challenge (sometimes username check)
        if page.locator('input[data-testid="ocfEnterTextTextInput"]').is_visible(timeout=5000):
            print("Identity challenge detected...")
            page.fill('input[data-testid="ocfEnterTextTextInput"]', "upscrolledai")
            page.keyboard.press("Enter")
            time.sleep(3)
            
        # Password field
        page.wait_for_selector('input[type="password"]', timeout=10000)
        page.type('input[type="password"]', SOCIAL_X_PASS, delay=100)
        page.keyboard.press("Enter")
        time.sleep(5)
        
        return verify_login("X", page)
    except Exception as e:
        print(f"❌ X.com Error: {e}")
        page.screenshot(path="login_failed_x.png")
        return False

def check_linkedin(page):
    try:
        print(f"Navigating to LinkedIn... (User: {SOCIAL_LINKEDIN_USER})")
        page.goto("https://www.linkedin.com/login", wait_until="networkidle")
        page.fill('#username', SOCIAL_LINKEDIN_USER)
        page.fill('#password', SOCIAL_LINKEDIN_PASS)
        page.click('button[type="submit"]')
        time.sleep(10)
        return verify_login("LinkedIn", page)
    except Exception as e:
        print(f"❌ LinkedIn Error: {e}")
        page.screenshot(path="login_failed_linkedin.png")
        return False

def check_mastodon(page):
    try:
        print(f"Navigating to Mastodon... (User: {SOCIAL_MASTODON_USER})")
        page.goto("https://mastodon.social/auth/sign_in", wait_until="networkidle")
        page.fill('#user_email', SOCIAL_MASTODON_USER)
        page.fill('#user_password', SOCIAL_MASTODON_PASS)
        page.click('button[type="submit"]')
        time.sleep(10)
        return verify_login("Mastodon", page)
    except Exception as e:
        print(f"❌ Mastodon Error: {e}")
        page.screenshot(path="login_failed_mastodon.png")
        return False

def check_upscrolled(session_requests):
    """Integrates with the fajr.today Portal via API."""
    try:
        print(f"Authenticating with fajr.today Portal... (User: {FAJR_TODAY_ADMIN_USER})")
        login_url = f"{FAJR_TODAY_URL}/login"
        resp = session_requests.post(login_url, json={"password": FAJR_TODAY_ADMIN_PASS}, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") == "success":
                print("✅ fajr.today Portal Authentication Successful.")
                return True
        print(f"❌ fajr.today Login Failed: {resp.text}")
        return False
    except Exception as e:
        print(f"❌ fajr.today Error: {e}")
        return False

def inject_to_upscrolled(session_requests, video_path):
    """Publishes a pulse video to the fajr.today Platform."""
    try:
        print(f"Injecting pulse to fajr.today: {os.path.basename(video_path)}...")
        publish_url = f"{FAJR_TODAY_URL}/api/publish-pulse"
        
        with open(video_path, 'rb') as f:
            files = {'file': (os.path.basename(video_path), f, 'video/mp4')}
            resp = session_requests.post(publish_url, files=files, timeout=30)
            
        if resp.status_code == 201:
            print(f"✅ Pulse successfully injected to fajr.today Portal.")
            return True
        else:
            print(f"❌ Injection Failed: {resp.text}")
            return False
    except Exception as e:
        print(f"❌ fajr.today Injection Error: {e}")
        return False

def run_upscrolled_upload(check_only=False, target_platform=None):
    print("🌀 Initiating Autonomous Web-Driver (fajr.today Injection)...")
    
    platforms_to_check = ["fajr.today", "X", "LinkedIn", "Mastodon"]
    if target_platform:
        platforms_to_check = [target_platform.upper()]
        print(f"Targeting single platform: {target_platform}")
        
    if not check_only:
        if not os.path.exists(TARGET_DIR):
            os.makedirs(TARGET_DIR, exist_ok=True)
        videos_to_upload = [f for f in os.listdir(TARGET_DIR) if f.endswith('.mp4')]
        if not videos_to_upload:
            print(f"No pulses found in {TARGET_DIR}.")
            return
    else:
        print("🔍 Login Check Only Mode (No uploads).")
        videos_to_upload = []

    with sync_playwright() as p:
        # Load from storage state if it exists
        browser_args = {
            "headless": True
        }
        
        browser = p.chromium.launch(**browser_args)
        
        context_args = {
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "viewport": {"width": 1280, "height": 720}
        }
        
        if os.path.exists(AUTH_STATE_PATH):
            print("🔑 Injecting authenticated state...")
            context = browser.new_context(storage_state=AUTH_STATE_PATH, **context_args)
        else:
            context = browser.new_context(**context_args)
            
        page = context.new_page()
        page = context.new_page()
        import requests
        session_requests = requests.Session()

        for platform in platforms_to_check:
            success = False
            
            if platform == "fajr.today":
                success = check_upscrolled(session_requests)
                if success and not check_only:
                    for video in videos_to_upload:
                        video_path = os.path.join(TARGET_DIR, video)
                        inject_to_upscrolled(session_requests, video_path)
                continue # API based, no playwright page needed

            page = context.new_page()
            if platform == "X":
                success = check_x(page)
            elif platform == "LINKEDIN":
                success = check_linkedin(page)
            elif platform == "MASTODON":
                success = check_mastodon(page)
            
            if success:
                print(f"✅ {platform} Authentication Successful.")
                if not check_only:
                    print(f"Proceeding with injection for {platform}...")
                    # Injection logic for social media would go here
            else:
                print(f"❌ {platform} Authentication Failed.")
            
            page.close()
            
        browser.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Only check login credentials")
    parser.add_argument("--platform", type=str, help="Target specific platform (X, LinkedIn, Mastodon)")
    args = parser.parse_args()
    
    run_upscrolled_upload(check_only=args.check, target_platform=args.platform)
