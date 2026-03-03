import os
import sys
import time
import re
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

PROFILE_DIR = os.path.join(ACTIVE_ROOT, 'scripts', 'data', 'x_profile')

def check_x_persistent():
    """Login to X.com using a persistent browser profile to bypass bot detection.
    Runs its own Playwright context with a user data dir to look like a real browser.
    Returns True if login verified."""
    with sync_playwright() as pw:
        os.makedirs(PROFILE_DIR, exist_ok=True)
        print(f"🔑 Launching persistent X.com context... (User: {SOCIAL_X_EMAIL})")
        context = pw.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            headless=False,
            slow_mo=120,
            args=["--disable-blink-features=AutomationControlled"],
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = context.pages[0] if context.pages else context.new_page()
        
        try:
            # Try home first — persistent profile may already be logged in
            page.goto("https://x.com/home", wait_until="domcontentloaded", timeout=20000)
            time.sleep(3)
            if page.url and "home" in page.url:
                if verify_login("X", page):
                    print("✅ X.com: Persistent session is valid.")
                    context.storage_state(path=AUTH_STATE_PATH)
                    context.close()
                    return True
            
            # Cold login
            print("Attempting cold login to X.com...")
            page.goto("https://x.com/login", wait_until="domcontentloaded", timeout=20000)
            time.sleep(4)
            
            # Wait for the username/email input (X.com shows a modal — target by placeholder)
            try:
                page.wait_for_selector('input[placeholder*="email" i], input[autocomplete="username"]', timeout=20000)
            except:
                print("⚠️ Username input not found — may need manual intervention.")
                page.screenshot(path="login_failed_x.png")
                context.close()
                return False
            
            page.type('input[placeholder*="email" i], input[autocomplete="username"]', SOCIAL_X_EMAIL, delay=150)
            # Click Next button
            try:
                page.click('[role="button"]:has-text("Next"), button:has-text("Next")', timeout=5000)
            except:
                page.keyboard.press("Enter")
            time.sleep(4)
            
            # Identity / username challenge
            try:
                page.wait_for_selector('input[data-testid="ocfEnterTextTextInput"]', timeout=5000)
                print("Identity challenge detected — entering handle...")
                page.fill('input[data-testid="ocfEnterTextTextInput"]', "upscrolledai")
                page.keyboard.press("Enter")
                time.sleep(3)
            except:
                pass  # No challenge, proceed
            
            # Password
            try:
                page.wait_for_selector('input[type="password"]', timeout=15000)
                page.type('input[type="password"]', SOCIAL_X_PASS, delay=150)
                page.keyboard.press("Enter")
                time.sleep(6)
            except Exception as e:
                print(f"❌ Password field error: {e}")
                page.screenshot(path="login_failed_x.png")
                context.close()
                return False
            
            success = verify_login("X", page)
            if not success:
                print("⚠️ X.com login failed.")
                if globals().get('IS_ROBOT'):
                    print("🤖 Robot: Authentication failed. I speak out about my disempowerment to the human loving person.")
                    page.screenshot(path="x_robot_disempowered.png")
                else:
                    print("💡 Suggestion: Check credentials or re-run with --robot for auto-failover.")
                
                context.close()
                return False
            
            print("✅ X.com session secured.")
            os.makedirs(os.path.dirname(AUTH_STATE_PATH), exist_ok=True)
            context.storage_state(path=AUTH_STATE_PATH)
            
            context.close()
            return success
        except Exception as e:
            print(f"❌ X.com Error: {e}")
            context.close()
            return False

def check_x(page):
    """Wrapper for compatibility — delegates to check_x_persistent."""
    return check_x_persistent()


def inject_x_posts(campaign_pulses, check_only=False):
    """Post each pulse video to @Upscrolledai on X.com.
    Uses stored session state to avoid persistent profile lock issues.
    
    campaign_pulses: list of dicts with keys: video_path, title, whydonate_url, identity_name
    """
    if not campaign_pulses:
        print("No pulses to inject to X.com.")
        return

    if not os.path.exists(AUTH_STATE_PATH):
        print(f"❌ No auth state found at {AUTH_STATE_PATH}. Run with --check first to authenticate.")
        return

    with sync_playwright() as pw:
        print(f"🐦 Launching X.com injection context (@Upscrolledai)...")
        browser = pw.chromium.launch(
            headless=False,
            slow_mo=150,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context(
            storage_state=AUTH_STATE_PATH,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720}
        )
        page = context.new_page()
        
        try:
            # Load home — session should be active from check_x_persistent
            page.goto("https://x.com/home", wait_until="domcontentloaded", timeout=20000)
            time.sleep(3)
            if not verify_login("X", page):
                print("❌ Session expired. Run --check first to re-authenticate.")
                context.close()
                return
            
            print(f"✅ Session valid. Injecting {len(campaign_pulses)} pulses...")
            
            for i, pulse in enumerate(campaign_pulses):
                video_path = pulse['video_path']
                title = pulse.get('title', 'Mutual Aid Gaza')
                wd_url = pulse.get('whydonate_url', '')
                identity = (pulse.get('identity_name') or 'Gaza Case').strip()
                if "PregnantA" in identity: identity = "Family in Gaza"
                if "Beneficiary" in identity: identity = "Survivor in Gaza"
                
                # Build tweet text with fajr.today brand
                en_title = title.split('|')[0].strip()[:80] if '|' in title else title[:80]
                tweet_text = f"{en_title}\n\n🔗 {wd_url}\n\n🌐 fajr.today\n#Gaza #MutualAid #Palestine"
                
                if check_only:
                    print(f"[DRY RUN] Would post: {en_title[:50]}...")
                    continue
                
                print(f"📤 Posting pulse {i+1}/{len(campaign_pulses)}: {identity}...")
                
                try:
                    # Navigate directly to compose URL
                    page.goto("https://x.com/compose/post", wait_until="domcontentloaded", timeout=15000)
                    time.sleep(3)
                    
                    # Handle cookie banner aggressively using evaluate to bypass pointer-interception
                    page.evaluate("""
                        const labels = ["Accept all cookies", "Refuse non-essential cookies", "Agree", "Understand", "Close"];
                        for (const label of labels) {
                            const btns = Array.from(document.querySelectorAll('button, div[role="button"]'));
                            const target = btns.find(b => b.innerText.includes(label));
                            if (target) {
                                target.click();
                                break;
                            }
                        }
                    """)
                    time.sleep(2)

                    # Dismiss any other overlays
                    page.keyboard.press("Escape")
                    time.sleep(1)
                    
                    # Re-verify we're on the compose page or open it
                    if not "/compose/post" in page.url:
                         page.goto("https://x.com/compose/post", wait_until="domcontentloaded", timeout=10000)
                         time.sleep(2)

                    # Wait for either the textarea or the placeholder
                    try:
                        page.wait_for_selector('[data-testid="tweetTextarea_0"], [aria-label="Post text"]', timeout=10000)
                    except:
                        # Sometimes it needs a click on the background or a re-nav
                        page.goto("https://x.com/compose/post", wait_until="networkidle")
                        time.sleep(3)

                    # 1. NUCLEAR CLEANING: Remove ALL internal IDs and placeholders
                    desc = pulse.get('description', '')
                    title = pulse.get('title', '')
                    iname = pulse.get('identity_name', '')
                    video_fname = os.path.basename(video_path)
                    
                    raw_text = f"{title} {desc}"
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

                    # Final Tweet Text
                    tweet_text = f"🎥 {hook_str}\n\n"
                    if clean_text:
                        # If we have a clean identity/title, show it prominently
                        display_name = iname if len(iname) > 3 and "Gaza Case" not in iname else ""
                        if display_name:
                             tweet_text = f"🎥 Pulse: {display_name}\n{hook_str}\n\n"
                        
                        if len(clean_text) < 140:
                             tweet_text += f"{clean_text}\n\n"
                    
                    tweet_text += f"🔗 Support: {wd_url}\n🌐 fajr.today\n#Gaza #Humanitarian"

                    # Type tweet text into the compose area
                    tweet_input = page.locator('[data-testid="tweetTextarea_0"], [aria-label="Post text"]').first
                    # Use force=True to bypass pointer-interception from overlays
                    tweet_input.click(force=True)
                    time.sleep(1)
                    page.keyboard.type(tweet_text, delay=40)
                    time.sleep(2)
                    
                    # Attach video
                    if os.path.exists(video_path):
                        print(f"⏳ Uploading video: {os.path.basename(video_path)}...")
                        try:
                            # X.com video input is often hidden or dynamic
                            file_input = page.locator('input[type="file"][data-testid="fileInput"]').first
                            file_input.set_input_files(video_path)
                            time.sleep(15) # Wait for processing
                        except Exception as v_err:
                            print(f"⚠️ Video upload failed: {v_err}")

                    # Submit tweet with multiple fallbacks
                    print("🚀 Submitting post...")
                    page.keyboard.press("Control+Enter")
                    time.sleep(2)
                    
                    # JS Fallback if still on compose page
                    if "/compose/post" in page.url:
                        page.evaluate("""
                            const btn = document.querySelector('[data-testid="tweetButton"], [data-testid="tweetButtonInline"]');
                            if (btn) btn.click();
                            else {
                                const btns = Array.from(document.querySelectorAll('button, div[role="button"]'));
                                const post = btns.find(b => b.innerText.includes('Post') || b.innerText.includes('Publicar'));
                                if (post) post.click();
                            }
                        """)
                        time.sleep(5)

                    if "/compose/post" not in page.url or page.locator('[data-testid="tweetTextarea_0"]').count() == 0:
                        print(f"✅ Posted: {identity}")
                    else:
                        print(f"⚠️ Post button might have failed for {identity}")
                    
                    # Rate limit courtesy delay
                    if i < len(campaign_pulses) - 1:
                        print("⏱️ Cooling down 25s before next post...")
                        time.sleep(25)
                        
                except Exception as post_err:
                    print(f"❌ Failed to post {identity}: {post_err}")
                    page.screenshot(path=f"x_post_failed_{i}.png")
                    continue
                    
        except Exception as e:
            print(f"❌ X injection error: {e}")
        finally:
            context.close()
    
    print("🌀 X.com injection complete.")



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

def check_portal(session_requests):
    """Integrates with our internal fajr.today Portal via API."""
    try:
        print(f"🤖 Robot: Authenticating with fajr.today Portal... (User: {FAJR_TODAY_ADMIN_USER})")
        login_url = f"{FAJR_TODAY_URL}/login"
        resp = session_requests.post(login_url, json={"password": FAJR_TODAY_ADMIN_PASS}, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") == "success":
                print("✅ Portal Authentication Successful.")
                return True
        
        err_msg = f"❌ Portal Login Failed: {resp.text}"
        print(err_msg)
        if globals().get('IS_ROBOT'):
            print("🤖 Robot: I failed to reach the Portal. I speak out about my disempowerment to the human loving person.")
        return False
    except Exception as e:
        print(f"❌ Portal Error: {e}")
        return False

def inject_to_portal(session_requests, video_path):
    """Publishes a pulse video to our internal fajr.today Portal."""
    try:
        print(f"🤖 Robot: Injecting pulse to Portal: {os.path.basename(video_path)}...")
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

def run_upscrolled_upload(check_only=False, target_platform=None, limit=None):
    """Main entry point for platform injections."""
    # ... logic to get pulses ...
    # (Checking the actual code is better)
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

    import requests
    session_requests = requests.Session()

    # --- X.com: uses its own dedicated persistent context ---
    if "X" in platforms_to_check:
        from generate_post_review import load_pulses
        all_pulses = load_pulses()
        if limit:
            all_pulses = all_pulses[:limit]
            
        # Transform for inject_x_posts
        campaign_pulses = []
        for p in all_pulses:
            campaign_pulses.append({
                'video_path': os.path.join(TARGET_DIR, p['video']),
                'title': p['title'],
                'whydonate_url': p['link'],
                'identity_name': p['identity'],
                'description': p['description']
            })
            
        inject_x_posts(campaign_pulses, check_only=check_only)
        platforms_to_check = [p for p in platforms_to_check if p != "X"]
    
    # --- fajr.today Portal (Internal Reliable Core) ---
    if "fajr.today" in platforms_to_check:
        success = check_portal(session_requests)
        if success and not check_only:
            for video in videos_to_upload:
                inject_to_portal(session_requests, os.path.join(TARGET_DIR, video))
        elif success:
            print("✅ Portal Authentication Successful.")
        else:
            print("❌ Portal Authentication Failed.")
        platforms_to_check = [p for p in platforms_to_check if p != "fajr.today"]

    # --- LinkedIn, Mastodon: shared playwright context ---
    if not platforms_to_check:
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=100)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720}
        )

        for platform in platforms_to_check:
            success = False
            page = context.new_page()
            if platform == "LINKEDIN":
                success = check_linkedin(page)
            elif platform == "MASTODON":
                success = check_mastodon(page)
            
            if success:
                print(f"✅ {platform} Authentication Successful.")
                if not check_only:
                    print(f"Proceeding with injection for {platform}...")
            else:
                print(f"❌ {platform} Authentication Failed.")
            page.close()
            
        browser.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Only check login credentials")
    parser.add_argument("--platform", type=str, help="Target specific platform (X, LinkedIn, Mastodon)")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of pulses to inject")
    parser.add_argument("--robot", action="store_true", help="100%% autonomous mode (no manual assist)")
    args = parser.parse_args()
    
    IS_ROBOT = args.robot # Global flag for robot behavior
    if IS_ROBOT:
        print("🤖 ROBOT MODE ACTIVE: 100% Autonomous execution in the 'Pot'.")
    
    run_upscrolled_upload(check_only=args.check, target_platform=args.platform, limit=args.limit)
