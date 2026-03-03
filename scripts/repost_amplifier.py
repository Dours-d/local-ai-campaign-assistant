import os
import sys
import time
import random
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

# Reconfigure stdout for UTF-8
sys.stdout.reconfigure(encoding='utf-8')

ACTIVE_ROOT = os.getcwd()
ENV_PATH = os.path.join(ACTIVE_ROOT, '.env.social')
load_dotenv(ENV_PATH)

# Account #2 Credentials (USER MUST PROVIDE THESE IN .env.social)
# For now, we assume a placeholder or that the user will update .env.social
# If SOCIAL_X_USER_2 is not set, it will fail gracefully or wait for input.
X2_USER = os.environ.get('SOCIAL_X_USER_2', 'YOUR_HANDLE_2')
X2_PASS = os.environ.get('SOCIAL_X_PASS_2', 'YOUR_PASS_2')
X2_EMAIL = os.environ.get('SOCIAL_X_EMAIL_2', 'YOUR_EMAIL_2')

MAIN_ACCOUNT = "Upscrolledai"
HANDLES_FILE = os.path.join(ACTIVE_ROOT, 'scripts', 'outreach_handles.txt')
PROFILE_DIR = os.path.join(ACTIVE_ROOT, 'scripts', 'data', 'x2_profile')

def get_target_handles():
    if not os.path.exists(HANDLES_FILE):
        return ["@fajrtoday"] # Default fallback
    with open(HANDLES_FILE, 'r') as f:
        return [line.strip() for line in f if line.strip().startswith('@')]

def run_amplifier():
    with sync_playwright() as pw:
        os.makedirs(PROFILE_DIR, exist_ok=True)
        print(f"🚀 Launching Amplifier Account (@{X2_USER})...")
        
        context = pw.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            headless=False,
            slow_mo=150,
            args=["--disable-blink-features=AutomationControlled"],
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        )
        page = context.pages[0]
        
        # 1. Login Logic
        print(f"🔑 Navigating to X.com login for @Abd_Al_Haadi...")
        try:
            page.goto("https://x.com/login", wait_until="domcontentloaded", timeout=120000)
            time.sleep(5)
        except Exception as e:
            print(f"⚠️ Navigation warning: {e}. Attempting to continue...")
        
        if "home" in page.url:
             print("✅ Already logged in.")
        else:
             print("📢 PLEASE PERFORM MANUAL LOGIN/2FA in the opened window.")
             print("⏳ Waiting up to 10 minutes for successful session...")
             try:
                 # Check every 10 seconds for the dashboard
                 for _ in range(60): 
                     if page.locator('[data-testid="SideNav_NewTweet_Button"]').count() > 0:
                         print("✅ Authentication verified.")
                         break
                     time.sleep(10)
                 else:
                     raise Exception("Auth Timeout")
             except Exception as e:
                 print(f"❌ Auth Timeout or Error: {e}")
                 print("💡 Window will stay open for manual check. Close it yourself when done.")
                 time.sleep(3600) # Keep open for an hour so user can see it
                 return

        # 2. Scrape Main Account for latest post IDs
        print(f"🔍 Monitoring @{MAIN_ACCOUNT} for new pulses...")
        target_handles = get_target_handles()
        
        # We'll pulse in a loop
        processed_post_ids = set()
        
        try:
            while True:
                page.goto(f"https://x.com/{MAIN_ACCOUNT}", timeout=30000)
                time.sleep(5)
                
                # Find all post articles
                posts = page.locator('article[data-testid="tweet"]').all()
                print(f"Found {len(posts)} posts on timeline.")
                
                for post in posts[:5]: # Check latest 5
                    try:
                        # Extract post ID / Link
                        link = post.locator('a[href*="/status/"]').first.get_attribute('href')
                        post_id = link.split('/')[-1]
                        
                        if post_id not in processed_post_ids:
                            print(f"🎬 New Pulse detected: {post_id}")
                            
                            # 1. REPOST
                            post.locator('[data-testid="retweet"]').first.click()
                            time.sleep(2)
                            page.locator('[data-testid="retweetConfirm"]').first.click()
                            time.sleep(3)
                            print(f"✅ Reposted: {post_id}")
                            
                            # 2. COMMENT (Tag handles with rich context)
                            post.locator('[data-testid="reply"]').first.click()
                            time.sleep(3)
                            
                            # Rich Contextual Comments
                            comment_variations = [
                                "STANDING TOGETHER. We fulfill our Amanah by amplifying these direct voices of resilience.",
                                "DIRECT PRESERVATION. Every pulse represents a soul standing firm against scarcity. We remember.",
                                "SOVEREIGN SUPPORT. Bypassing the filters of silence to uphold the dignity of Gaza's families.",
                                "WITNESSING TRUTH. Beyond the automated filters lies the unyielding spirit of Gaza.",
                                "AMANA IN ACTION. Your support directly preserves life and dignity where it is most needed."
                            ]
                            
                            # Tag 3-5 random handles
                            sampled_handles = random.sample(target_handles, min(5, len(target_handles)))
                            tags = " ".join(sampled_handles)
                            base_comment = random.choice(comment_variations)
                            reply_text = f"{base_comment}\n\n{tags}\n#fajrtoday #PreserveGaza"
                            
                            page.locator('[data-testid="tweetTextarea_0"]').first.fill(reply_text)
                            time.sleep(2)
                            page.locator('[data-testid="tweetButtonInline"]').first.click()
                            time.sleep(4)
                            print(f"💬 Commented with tags on : {post_id}")
                            
                            processed_post_ids.add(post_id)
                        
                    except Exception as e:
                        print(f"⚠️ Error processing post: {e}")
                        continue
                
                print("⏳ Sleeping for 5 minutes before next check...")
                time.sleep(300) 
        except Exception as e:
            print(f"❌ Monitor Loop Error: {e}")
            context.close()

if __name__ == "__main__":
    run_amplifier()
