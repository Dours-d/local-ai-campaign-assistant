import os
import sys
import time
from playwright.sync_api import sync_playwright

# ==========================================
# VECTOR 12: THE AUTONOMOUS WEB-DRIVER (MEDIUM)
# ==========================================
# This script automates the uploading of the generated Long-Form
# rhetorical essays directly to Medium.com. It requires credentials 
# to be set in the environment variables to function as a burner node.
# ==========================================

ACTIVE_ROOT = os.environ.get('ACTIVE_ROOT', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TARGET_DIR = os.path.join(ACTIVE_ROOT, 'vault', 'amplification', 'longform')

MEDIUM_EMAIL = os.environ.get('MEDIUM_EMAIL', 'test@example.com')
MEDIUM_PASS = os.environ.get('MEDIUM_PASS', 'test_password')

def run_medium_upload():
    print("🌀 Initiating Autonomous Web-Driver (Medium Long-Form Injection)...")
    
    if MEDIUM_EMAIL == 'test@example.com':
        print("⚠️ WARNING: MEDIUM_EMAIL not set. Please set environment variables to authenticate as your generic outpost.")
        
    essays_to_publish = [f for f in os.listdir(TARGET_DIR) if f.endswith('.md')]
    
    if not essays_to_publish:
        print(f"No long-form archives found in {TARGET_DIR}.")
        return

    print(f"Found {len(essays_to_publish)} essays ready for autonomous publication.")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False) # Keep headed for monitoring
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720}
        )
        page = context.new_page()

        try:
            print("Navigating to Medium.com...")
            # Note: Medium has complex auth flows (often email links). 
            # For burner nodes, Twitter/Google SSO or standard email-password (if available) is preferred.
            # This follows a standard email/password fallback DOM model.
            page.goto("https://medium.com/m/signin")
            
            print("Authenticating burner node...")
            # We look for the "Sign in with email" flow if it exists
            if page.locator('text="Sign in with email"').is_visible():
                page.locator('text="Sign in with email"').click()
                page.fill('input[type="email"]', MEDIUM_EMAIL)
                page.click('button:has-text("Continue")')
            
            # Note: If Medium forces a magic link, the script will pause here.
            # Automated email reading via IMAP could bypass magic links, but is out of scope 
            # for the basic injector model. We assume the operator approves the auth if needed once.
            
            # Wait for dashboard to confirm auth success
            page.wait_for_selector('a[aria-label="Write"]', timeout=30000)
            print("Authentication successful.")

            for essay in essays_to_publish:
                filepath = os.path.join(TARGET_DIR, essay)
                print(f"Injecting philosophical payload: {essay}...")
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Separate a title if possible (based on Llama3 markdown output)
                lines = content.split('\n')
                title = lines[0].replace('#', '').strip() if lines[0].startswith('#') else "Sovereign Trust: A Reflection"
                body = '\n'.join(lines[1:]).strip()

                # Navigate to the editor
                page.click('a[aria-label="Write"]')
                page.wait_for_selector('div[data-first-node="true"]', timeout=10000)
                
                # Fill Title
                page.keyboard.type(title)
                page.keyboard.press('Enter')
                
                # Fill Body (Medium's editor is complex blockwise, standard pasting is most reliable)
                page.keyboard.insert_text(body)
                
                # Initiate Publishing flow
                page.click('button:has-text("Publish")')
                
                # Add Tags (Medium allows up to 5)
                page.wait_for_selector('input[placeholder="Add a topic"]')
                tags = ["MutualAid", "HumanRights", "Geopolitics", "Solidarity", "Philanthropy"]
                for tag in tags:
                    page.fill('input[placeholder="Add a topic"]', tag)
                    page.keyboard.press('Enter')
                    time.sleep(0.5)
                
                # Final Publish
                page.click('button[data-action="publish"]')
                print(f"✅ Long-Form Essay {essay} successfully anchored to Medium ecosystem.")
                
                # Rest between publications
                time.sleep(15)

        except Exception as e:
            print(f"\n❌ Web-Driver encountered an error: {e}")
            print("Medium's DOM may have changed or Magic Link authentication blocked the automated flow.")
        
        finally:
            print("Closing connection.")
            browser.close()

if __name__ == "__main__":
    if not os.path.exists(TARGET_DIR):
        print(f"Directory {TARGET_DIR} does not exist. Run Vector 12 Master Weaver first.")
        sys.exit(1)
    run_medium_upload()
