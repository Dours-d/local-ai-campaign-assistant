import re
import requests
import json
import websocket
import time
import os
import sys
import traceback
from PIL import Image

# Configure UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

CDP_URL = "http://127.0.0.1:9222/json"

class WhyDonateAutomator:
    global_msg_id = 100

    def __init__(self, cdp_url=CDP_URL):
        self.cdp_url = cdp_url
        self.ws = None

    def connect(self):
        try:
            r = requests.get(self.cdp_url)
            tabs = r.json()
            # Prefer existing WhyDonate page tabs
            target_tab = next((t for t in tabs if t.get('type') == 'page' and "whydonate.com" in t.get('url', '')), None)
            if not target_tab:
                # Try any page tab
                target_tab = next((t for t in tabs if t.get('type') == 'page'), tabs[0])
            
            self.ws = websocket.create_connection(target_tab['webSocketDebuggerUrl'])
            
            # Check login state
            url = self.get_url()
            if "login" in url or "wp-login.php" in url:
                print("DEBUG: Detected login page. Attempting automated login...", flush=True)
                self.perform_login()
            
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False

    def perform_login(self):
        from dotenv import load_dotenv
        load_dotenv()
        email = os.getenv("ADMIN_EMAIL")
        password = os.getenv("ADMIN_PASSWORD")
        
        js_fill = f"""
        (function() {{
            const emailField = document.getElementById('loginEmail') || document.querySelector('input[type="email"]') || document.getElementById('user_login');
            const passField = document.getElementById('loginPassword') || document.querySelector('input[type="password"]') || document.getElementById('user_pass');
            const btn = document.getElementById('userLogin') || document.getElementById('wp-submit') || 
                        Array.from(document.querySelectorAll('button')).find(b => b.innerText.trim().includes('Login'));
            if (emailField && passField && btn) {{
                emailField.value = {json.dumps(email)};
                emailField.dispatchEvent(new Event('input', {{bubbles:true}}));
                passField.value = {json.dumps(password)};
                passField.dispatchEvent(new Event('input', {{bubbles:true}}));
                btn.click();
                return "SUBMITTED";
            }}
            return "FIELDS_NOT_FOUND";
        }})()
        """
        status = self.run_js(js_fill)
        print(f"DEBUG: Login status: {status}", flush=True)
        time.sleep(10)

    def send_cdp(self, method, params=None):
        WhyDonateAutomator.global_msg_id += 1
        msg = {"id": WhyDonateAutomator.global_msg_id, "method": method, "params": params or {}}
        self.ws.send(json.dumps(msg))
        return WhyDonateAutomator.global_msg_id

    def recv_until_id(self, msg_id, timeout=10):
        start = time.time()
        while time.time() - start < timeout:
            res = json.loads(self.ws.recv())
            if res.get('id') == msg_id: return res
        return None

    def run_js(self, js):
        try:
            mid = self.send_cdp("Runtime.evaluate", {"expression": js, "returnByValue": True})
            res = self.recv_until_id(mid)
            if not res: return None
            return res.get('result', {}).get('result', {}).get('value')
        except Exception as e:
            print(f"DEBUG: run_js failed: {e}")
            return None

    def take_screenshot(self, filename):
        mid = self.send_cdp("Page.captureScreenshot", {"format": "png"})
        res = self.recv_until_id(mid)
        if res and 'result' in res:
            import base64
            with open(filename, "wb") as f:
                f.write(base64.b64decode(res['result']['data']))
            print(f"Screenshot saved to {filename}")

    def type_string(self, text):
        for char in text:
            self.send_cdp("Input.dispatchKeyEvent", {"type": "char", "text": char})
            time.sleep(0.05)

    def press_key(self, key, code):
        self.send_cdp("Input.dispatchKeyEvent", {"type": "keyDown", "key": key, "windowsVirtualKeyCode": code})
        self.send_cdp("Input.dispatchKeyEvent", {"type": "keyUp", "key": key, "windowsVirtualKeyCode": code})

    def upload_file(self, selector, file_path):
        try:
            res = self.send_cdp("DOM.getDocument")
            doc = self.recv_until_id(res)
            node_res = self.send_cdp("DOM.querySelector", {"nodeId": doc['result']['root']['nodeId'], "selector": selector})
            node = self.recv_until_id(node_res)
            if node and 'result' in node:
                self.send_cdp("DOM.setFileInputFiles", {"files": [file_path], "nodeId": node['result']['nodeId']})
                return True
        except: pass
        return False

    def get_url(self):
        return self.run_js("window.location.href")

    def get_step(self):
        try:
            body = self.run_js("document.body.innerText")
            if body is None: return 1
            
            # Step 4 check
            if any(x in body for x in ["Launch Fundraiser", "Launch and share", "Target amount", "Target Amount"]): return 4
            # Step 3 check
            if any(x in body for x in ["Fundraiser Title", "Fundraiser Story", "Your story", "Unique link"]): return 3
            # Step 2 check
            if any(x in body for x in ["Who is this fundraiser for?", "collecting money for?", "Someone Else"]): return 2
            # Step 1 check
            if any(x in body for x in ["What is your address", "which language do you prefer", "Let's Get Your Fundraiser Started"]): return 1
            
            # Login/Register check
            if any(x in body for x in ["Create New Account", "Login to your account", "Already have an account?"]) and \
               not any(x in body for x in ["Step 1/4", "Step 2/4", "Step 3/4", "Step 4/4"]):
                print("DEBUG: Detected Login/Register page. Session likely expired.", flush=True)
                return 0
            
            # Stepper check
            step_active = self.run_js("document.querySelector('mat-step-header[aria-selected=\"true\"]')?.innerText")
            if step_active:
                if "1" in step_active: return 1
                if "2" in step_active: return 2
                if "3" in step_active: return 3
                if "4" in step_active: return 4
        except Exception as e:
            print(f"DEBUG: get_step error: {e}", flush=True)
        return 1

    def fill_step1(self, item):
        step = self.get_step()
        print(f"DEBUG: fill_step1 start for {item['bid']}, current step: {step}", flush=True)
        if step == 0:
            print("ERROR: Detected Login/Register page. Please log in to Whydonate in the Edge browser first.", flush=True)
            return False
        if step >= 2:
            print("DEBUG: Already at Step 2 or later. Skipping Step 1 fill.", flush=True)
            return True
        
        # Select Category (CDP Mouse Click) - standard humanitarian for all
        print("DEBUG: Selecting Category...", flush=True)
        coords = self.run_js("""
            (function() {
                const target = Array.from(document.querySelectorAll('button, mat-card, .mat-mdc-card, .category-card, div, span'))
                    .find(el => el.innerText && (el.innerText.trim() === 'Humanitarian Aid' || el.innerText.trim().includes('Humanitarian')));
                if (target) {
                    target.scrollIntoView({behavior: "instant", block: "center"});
                    const rect = target.getBoundingClientRect();
                    return {x: rect.left + rect.width/2, y: rect.top + rect.height/2};
                }
                return null;
            })()
        """)
        if coords:
            self.send_cdp("Input.dispatchMouseEvent", {"type": "mousePressed", "x": coords['x'], "y": coords['y'], "button": "left", "clickCount": 1})
            self.send_cdp("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": coords['x'], "y": coords['y'], "button": "left", "clickCount": 1})
        time.sleep(3)

        # Type and select Porto, Portugal
        print("DEBUG: Typing 'Porto, Portugal'...", flush=True)
        self.run_js("""
            (function() {
                const i = document.querySelector('input[id^="mat-input-"]') || document.querySelector('input[placeholder*="Location"]');
                if (i) { i.value = ''; i.focus(); }
            })()
        """)
        self.type_string("Porto, Portugal")
        time.sleep(3)
        # Nudge navigation to ensure dropdown item selection
        for _ in range(2):
            self.send_cdp("Input.dispatchKeyEvent", {"type": "keyDown", "windowsVirtualKeyCode": 40}) # Down
            self.send_cdp("Input.dispatchKeyEvent", {"type": "keyUp", "windowsVirtualKeyCode": 40})
            time.sleep(0.5)
        self.send_cdp("Input.dispatchKeyEvent", {"type": "keyDown", "windowsVirtualKeyCode": 13}) # Enter
        self.send_cdp("Input.dispatchKeyEvent", {"type": "keyUp", "windowsVirtualKeyCode": 13})
        time.sleep(3)
        
        # Verify Location before next
        addr_val = self.run_js("(document.querySelector('input[id^=\"mat-input-\"]') || {}).value || ''")
        if "Porto" not in addr_val:
            print(f"DEBUG: Porto not detected (found: {addr_val}). Retrying Step 1 type...", flush=True)
            self.type_string("Porto, Portugal")
            time.sleep(2)
            self.send_cdp("Input.dispatchKeyEvent", {"type": "keyDown", "windowsVirtualKeyCode": 13})
            self.send_cdp("Input.dispatchKeyEvent", {"type": "keyUp", "windowsVirtualKeyCode": 13})
            time.sleep(3)
        
        self.take_screenshot(f"data/s1_ready_to_next_{item['bid']}.png")
        
        # Click Next
        print("DEBUG: Clicking Next in Step 1...", flush=True)
        for i in range(5):
             # Check if advanced already
            if self.get_step() >= 2: return True
            
            # Try JS enable and click first
            self.run_js("""
                (function() {
                    const btn = document.querySelector('button.mat-stepper-next') || 
                                document.getElementById('saveStep1') ||
                                Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Next'));
                    if (btn) {
                        btn.removeAttribute('disabled');
                        btn.click();
                    }
                })()
            """)
            time.sleep(3)
            if self.get_step() >= 2: 
                print("DEBUG: Advanced to Step 2 (via JS click).", flush=True)
                return True

            coords = self.run_js("""
                (function() {
                    const btn = document.querySelector('button.mat-stepper-next') || 
                                document.getElementById('saveStep1') ||
                                Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Next'));
                    if (btn) {
                        btn.scrollIntoView({behavior: "instant", block: "center"});
                        btn.removeAttribute('disabled');
                        const rect = btn.getBoundingClientRect();
                        return {x: rect.left + rect.width/2, y: rect.top + rect.height/2};
                    }
                    return null;
                })()
            """)
            if coords:
                self.send_cdp("Input.dispatchMouseEvent", {"type": "mousePressed", "x": coords['x'], "y": coords['y'], "button": "left", "clickCount": 1})
                self.send_cdp("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": coords['x'], "y": coords['y'], "button": "left", "clickCount": 1})
                time.sleep(5)
                if self.get_step() >= 2:
                     print("DEBUG: Advanced to Step 2 (via Mouse click).", flush=True)
                     return True
            time.sleep(2)
        return False


    def fill_step2(self, item):
        step = self.get_step()
        print(f"DEBUG: fill_step2 start for {item['bid']}, current step: {step}", flush=True)
        if step >= 3:
            print("DEBUG: Already at Step 3 or later. Skipping Step 2 fill.", flush=True)
            return True
            
        self.take_screenshot(f"data/verify_s2_start_{item['bid']}.png")
        
        # Decide if "Yourself" or "Someone Else"
        use_someone_else = True 
        beneficiary_name = item.get('beneficiary_name') or item.get('display_name')
        if not beneficiary_name:
            match = re.search(r"Help ([\w\s]+) and", item.get('title', ''), re.I)
            beneficiary_name = match.group(1).strip() if match else "Amir Al-Najjar"

        if use_someone_else:
            print(f"DEBUG: Selecting 'Someone Else' for {beneficiary_name}...", flush=True)
            # Find and click the card header or child element to ensure selection triggers
            self.run_js("""
                (function() {
                    const els = Array.from(document.querySelectorAll('*'));
                    const target = els.find(el => el.innerText && el.innerText.trim() === 'Someone Else' && el.offsetParent !== null);
                    if (target) {
                        const card = target.closest('mat-card, .mat-mdc-card, div[role="button"], .category-card');
                        if (card) {
                            card.scrollIntoView({behavior: "instant", block: "center"});
                            card.click();
                            // Click the text too for good measure
                            target.click();
                            return "CLICKED_BOTH";
                        }
                        target.click();
                        return "CLICKED_TEXT_ONLY";
                    }
                    return "NOT_FOUND";
                })()
            """)
            time.sleep(3)
            
            # Fill Name with character typing and then event dispatch
            print(f"DEBUG: Filling beneficiary name: {beneficiary_name}...", flush=True)
            coords = self.run_js(f"""
                (function() {{
                    const inputs = Array.from(document.querySelectorAll('input'));
                    const nameInput = inputs.find(i => i.id === 'name' || i.getAttribute('formcontrolname') === 'name' || i.placeholder?.includes('Name'));
                    if (nameInput) {{
                        nameInput.scrollIntoView({{behavior: "instant", block: "center"}});
                        nameInput.focus();
                        nameInput.select();
                        document.execCommand('delete', false, null); // Clear existing
                        const rect = nameInput.getBoundingClientRect();
                        return {{x: rect.left + rect.width/2, y: rect.top + rect.height/2}};
                    }}
                    return null;
                }})()
            """)
            if coords:
                self.send_cdp("Input.dispatchMouseEvent", {"type": "mousePressed", "x": coords['x'], "y": coords['y'], "button": "left", "clickCount": 1})
                self.send_cdp("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": coords['x'], "y": coords['y'], "button": "left", "clickCount": 1})
                self.type_string(beneficiary_name)
                time.sleep(1)
                # Dispatch events to be absolutely sure Angular picks it up
                self.run_js("""
                    (function() {
                        const i = document.getElementById('name') || document.querySelector('input[formcontrolname="name"]');
                        if (i) {
                            i.dispatchEvent(new Event('input', {bubbles:true}));
                            i.dispatchEvent(new Event('change', {bubbles:true}));
                            i.dispatchEvent(new Event('blur', {bubbles:true}));
                        }
                    })()
                """)
            else:
                print("DEBUG: Could not find name input for typing.", flush=True)
            time.sleep(2)
        else:
             # Logic for "Yourself" (not used for this batch normally)
             pass
            
        self.take_screenshot(f"data/verify_s2_selected_{item['bid']}.png")
        
        # Click Next
        print("DEBUG: Clicking Next in Step 2...", flush=True)
        for i in range(5):
            # Check if advanced already
            if self.get_step() >= 3: return True
            
            # Click the card once more just to be absolutely sure the model is updated
            self.run_js("""
                (function() {
                    const els = Array.from(document.querySelectorAll('*'));
                    const target = els.find(el => el.innerText && el.innerText.trim() === 'Someone Else' && el.offsetParent !== null);
                    if (target) target.click();
                })()
            """)
            time.sleep(1)

            # Try JS enable and click first
            self.run_js("""
                (function() {
                    const btn = document.getElementById('saveStep2') ||
                                document.querySelector('button.mat-stepper-next') || 
                                document.querySelector('.mat-stepper-next') ||
                                Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Next') || b.innerText.includes('Continue'));
                    if (btn) {
                        btn.removeAttribute('disabled');
                        btn.click();
                        return "CLICKED";
                    }
                    return "NOT_FOUND";
                })()
            """)
            time.sleep(4)
            if self.get_step() >= 3: 
                print("DEBUG: Advanced to Step 3 (via JS click).", flush=True)
                return True
            
            # Try Mouse click if JS failed
            coords = self.run_js("""
                (function() {
                    const btn = document.getElementById('saveStep2') ||
                                document.querySelector('button.mat-stepper-next') || 
                                Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Next') || b.innerText.includes('Continue'));
                    if (btn) {
                        btn.scrollIntoView({behavior: "instant", block: "center"});
                        const rect = btn.getBoundingClientRect();
                        return {x: rect.left + rect.width/2, y: rect.top + rect.height/2};
                    }
                    return null;
                })()
            """)
            if coords:
                self.send_cdp("Input.dispatchMouseEvent", {"type": "mousePressed", "x": coords['x'], "y": coords['y'], "button": "left", "clickCount": 1})
                self.send_cdp("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": coords['x'], "y": coords['y'], "button": "left", "clickCount": 1})
                time.sleep(6)
                if self.get_step() >= 3: 
                    print("DEBUG: Advanced to Step 3 (via Mouse click).", flush=True)
                    return True
            time.sleep(2)
        return False


    def fill_step3(self, item):
        step = self.get_step()
        print(f"DEBUG: fill_step3 start for {item['bid']}, current step: {step}", flush=True)
        if step >= 4:
            print("DEBUG: Already at Step 4 or later. Skipping Step 3 fill.", flush=True)
            return True
            
        print("Processing Step 3/4 (Content & Media)...", flush=True)
        self.take_screenshot(f"data/verify_s3_start_{item['bid']}.png")
        
        # 0. Title & Unique URL
        raw_title = item.get('title', 'Help support this campaign')
        # Filter out URLs from titles if they leaked in
        if "chuffed.org" in raw_title:
            raw_title = "Help Support This Worthy Campaign"
        title = raw_title[:70].strip()
        
        from datetime import datetime
        ts = datetime.now().strftime("%H%M%S")
        slug = f"f-{item['bid']}-{ts}"[:70] 
        
        print(f"DEBUG: Filling Step 3 Title: {title} and Slug: {slug}", flush=True)
        self.run_js(f"""
            (function() {{
                const t = document.querySelector('input[formcontrolname=\"title\"], input.fundraiserTitle');
                if (t) {{
                    t.focus();
                    t.value = {json.dumps(title)};
                    t.dispatchEvent(new Event('input', {{bubbles:true}}));
                    t.dispatchEvent(new Event('blur', {{bubbles:true}}));
                }}
                const u = document.querySelector('input[formcontrolname=\"custom_url\"], input.linkUrl');
                if (u) {{
                    u.focus();
                    u.removeAttribute('readonly');
                    u.value = {json.dumps(slug)};
                    u.dispatchEvent(new Event('input', {{bubbles:true}}));
                    u.dispatchEvent(new Event('blur', {{bubbles:true}}));
                }}
            }})()
        """)
        time.sleep(2)

        # 1. Fill Story
        description = item.get('campaign_description') or item.get('description') or item.get('story') or "Help support this campaign. We need your support to rebuild lives."
        if len(description) < 15: description += " Please help us support this worthy cause."
        
        print(f"DEBUG: Filling Description ({len(description)} chars)...", flush=True)
        # Try to click the story area first to activate it
        self.run_js("const s = document.getElementById('createFundraiserStoryDescription') || document.querySelector('.ql-editor'); if(s) s.click();")
        time.sleep(2)
        
        story_res = self.run_js(f"""
            (function() {{
                const ta = document.querySelector('textarea.createFundraiserStory, textarea[formcontrolname=\"description\"]');
                if (ta) {{
                    ta.focus();
                    ta.value = {json.dumps(description)};
                    ta.dispatchEvent(new Event('input', {{bubbles:true}}));
                    return "STORY_SET_TEXTAREA";
                }}
                const editor = document.querySelector('.ql-editor');
                if (editor) {{
                    editor.innerHTML = '<p>' + {json.dumps(description)} + '</p>';
                    editor.dispatchEvent(new Event('input', {{bubbles:true}}));
                    editor.dispatchEvent(new Event('blur', {{bubbles:true}}));
                    return "STORY_SET_QL";
                }}
                return "STORY_NOT_FOUND";
            }})()
        """)
        print(f"DEBUG: Story filling result: {story_res}", flush=True)
        time.sleep(2)
        
        # 2. Upload Image
        img_url = item.get('image') or item.get('image_url')
        if img_url:
            img_path = os.path.abspath(img_url if os.path.exists(img_url) else f"data/temp_{item['bid']}.jpg")
            try:
                if not os.path.exists(img_path):
                    r = requests.get(img_url, timeout=10)
                    if r.status_code == 200:
                        with open(img_path, 'wb') as f: f.write(r.content)
                print(f"DEBUG: Uploading image {img_path}", flush=True)
                self.upload_file('input[type="file"]', img_path)
                time.sleep(8)
                
                # Handle potential Crop Modal
                print("DEBUG: Checking for Crop/Save Button...", flush=True)
                self.run_js("""
                    (function() {
                        const btns = Array.from(document.querySelectorAll('button'));
                        const saveCrop = btns.find(b => b.innerText.includes('Save') || b.innerText.includes('Apply') || b.innerText.includes('Crop'));
                        if (saveCrop) { saveCrop.click(); return "CROP_CLICKED"; }
                        return "NO_CROP_MODAL";
                    })()
                """)
                time.sleep(3)
            except Exception as e: print(f"Image failed: {e}")

        self.take_screenshot(f"data/verify_s3_filled_{item['bid']}.png")
        # Click Next
        print("DEBUG: Clicking Next in Step 3...", flush=True)
        for i in range(5):
            coords = self.run_js("""
                (function() {
                    const btn = document.getElementById('saveStep3') ||
                                document.querySelector('button.mat-stepper-next') ||
                                Array.from(document.querySelectorAll('button'))
                                .find(b => (b.innerText.includes('Next') || b.innerText.includes('Continue') || b.classList.contains('mat-stepper-next')));
                    if (btn) {
                        btn.scrollIntoView({behavior: "instant", block: "center"});
                        btn.removeAttribute('disabled');
                        const rect = btn.getBoundingClientRect();
                        return {x: rect.left + rect.width/2, y: rect.top + rect.height/2};
                    }
                    return null;
                })()
            """)
            if coords:
                self.send_cdp("Input.dispatchMouseEvent", {"type": "mousePressed", "x": coords['x'], "y": coords['y'], "button": "left", "clickCount": 1})
                self.send_cdp("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": coords['x'], "y": coords['y'], "button": "left", "clickCount": 1})
                time.sleep(6)
                if self.get_step() >= 4: 
                    print("DEBUG: Advanced to Step 4.", flush=True)
                    return True
            time.sleep(2)
        return False

    def finalize_campaign(self, item):
        print(f"DEBUG: finalize_campaign start for {item['bid']}", flush=True)
        # Success guard: Check if already finished
        final_url = self.get_url()
        if "whydonate.com/fundraising/" in final_url and "/create" not in final_url and "/start" not in final_url:
            print(f"DEBUG: Already on a final campaign page: {final_url}. Skipping finalize.", flush=True)
            return True
            
        print("Finalizing Campaign (Step 4)...", flush=True)
        goal = str(item.get('goal', 2500))
        
        # 0. Select Currency (Euro)
        print("DEBUG: Selecting Euro as currency...", flush=True)
        self.run_js("""
            (function() {
                const currencySelect = document.querySelector('mat-select[formcontrolname="currency_id"]') || 
                                     document.querySelector('mat-select');
                if (currencySelect) {
                    currencySelect.click();
                    setTimeout(() => {
                        const euroOption = Array.from(document.querySelectorAll('mat-option'))
                            .find(o => o.innerText.includes('EUR') || o.innerText.includes('Euro'));
                        if (euroOption) euroOption.click();
                    }, 500);
                }
            })()
        """)
        time.sleep(2)

        # 1. Fill Goal with nudging (Clear first)
        coords = self.run_js(f"""
            (function() {{
                const g = document.querySelector('input[formcontrolname="target_amount"]') || 
                          document.querySelector('input[placeholder*="Target"]');
                if (g) {{
                    g.scrollIntoView({{behavior: "instant", block: "center"}});
                    g.value = ""; // Clear existing
                    g.dispatchEvent(new Event('input', {{bubbles:true}}));
                    const rect = g.getBoundingClientRect();
                    return {{x: rect.left + rect.width/2, y: rect.top + rect.height/2}};
                }}
                return null;
            }})()
        """)
        if coords:
            print(f"DEBUG: Typing goal {goal}...", flush=True)
            self.send_cdp("Input.dispatchMouseEvent", {"type": "mousePressed", "x": coords['x'], "y": coords['y'], "button": "left", "clickCount": 1})
            self.send_cdp("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": coords['x'], "y": coords['y'], "button": "left", "clickCount": 1})
            time.sleep(1)
            # Use backspaces to be absolutely sure it's clear if JS clear failed
            for _ in range(10):
                self.send_cdp("Input.dispatchKeyEvent", {"type": "rawKeyDown", "windowsVirtualKeyCode": 8})
                self.send_cdp("Input.dispatchKeyEvent", {"type": "keyUp", "windowsVirtualKeyCode": 8})
            self.type_string(goal)
            time.sleep(1)
            self.send_cdp("Input.dispatchKeyEvent", {"type": "keyDown", "windowsVirtualKeyCode": 13})
            self.send_cdp("Input.dispatchKeyEvent", {"type": "keyUp", "windowsVirtualKeyCode": 13})
        
        # 2. Checkboxes (Nudge them)
        self.run_js("""
            (function() {
                document.querySelectorAll('mat-checkbox').forEach(box => {
                    const input = box.querySelector('input');
                    if (input && !input.checked) {
                        box.click();
                    }
                });
            })()
        """)
        time.sleep(1)

        # 3. Disable End Date (Slide Toggle)
        print("DEBUG: Disabling End Date/Date Range toggle if active...", flush=True)
        toggle_status = self.run_js("""
            (function() {
                const els = Array.from(document.querySelectorAll('*'));
                const label = els.find(el => el.innerText && el.innerText.trim() === 'Set date range');
                if (label) {
                    const row = label.closest('div, mat-list-item, .flex');
                    const toggle = row?.querySelector('mat-slide-toggle, mat-checkbox, .mat-mdc-slide-toggle');
                    if (toggle) {
                        const isChecked = toggle.getAttribute('aria-checked') === 'true' || 
                                         toggle.classList.contains('mat-checked') || 
                                         toggle.classList.contains('mat-mdc-slide-toggle-checked');
                        if (isChecked) {
                            toggle.scrollIntoView({behavior: "instant", block: "center"});
                            // Click the toggle or its button
                            const btn = toggle.querySelector('button') || toggle;
                            btn.click();
                            return "TOGGLED_OFF";
                        }
                        return "ALREADY_OFF";
                    }
                    return "LABEL_FOUND_BUT_NO_TOGGLE";
                }
                return "LABEL_NOT_FOUND";
            })()
        """)
        print(f"DEBUG: Toggle Status: {toggle_status}", flush=True)
        time.sleep(2)
        self.take_screenshot(f"data/verify_s4_{item['bid']}.png")
        
        # Click Finish / Start (Highlight then Validate)
        print("DEBUG: Clicking Finish in Step 4 (Highlight then Validate)...", flush=True)
        for i in range(5):
            coords = self.run_js("""
                (function() {
                    const btn = Array.from(document.querySelectorAll('button'))
                        .find(b => b.innerText.includes('Finish') || 
                                   b.innerText.includes('Launch Fundraiser') || 
                                   b.innerText.includes('Start Fundraiser') ||
                                   b.innerText.includes('Next'));
                    if (btn) {
                        btn.scrollIntoView({behavior: "instant", block: "center"});
                        btn.removeAttribute('disabled');
                        const rect = btn.getBoundingClientRect();
                        return {x: rect.left + rect.width/2, y: rect.top + rect.height/2};
                    }
                    return null;
                })()
            """)
            if coords:
                # Highlight
                self.send_cdp("Input.dispatchMouseEvent", {"type": "mousePressed", "x": coords['x'], "y": coords['y'], "button": "left", "clickCount": 1})
                self.send_cdp("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": coords['x'], "y": coords['y'], "button": "left", "clickCount": 1})
                time.sleep(1)
                # Validate
                self.send_cdp("Input.dispatchMouseEvent", {"type": "mousePressed", "x": coords['x'], "y": coords['y'], "button": "left", "clickCount": 1})
                self.send_cdp("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": coords['x'], "y": coords['y'], "button": "left", "clickCount": 1})
            
            # Watch for terminal redirect
            for _ in range(12): 
                time.sleep(5)
                final_url = self.get_url()
                print(f"DEBUG: Watch Final URL (Attempt {_+1}/12): {final_url}", flush=True)
                # Success if slug exists and not just /start or /create
                if "whydonate.com/fundraising/" in final_url and \
                   "/create" not in final_url and \
                   "/start" not in final_url and \
                   len(final_url.split('/')[-1]) > 5:
                    print(f"SUCCESS: Campaign created at {final_url}", flush=True)
                    self.take_screenshot(f"data/success_{item['bid']}.png")
                    with open("data/success_campaigns.txt", "a") as f: f.write(f"{item['bid']}|{final_url}\n")
                    return True
                
                # Check for redirects back to step 1 (error state)
                curr_step = self.get_step()
                if curr_step == 1:
                    print(f"DEBUG: Redirected back to Step 1. Error likely occurred.", flush=True)
                    break

            print(f"DEBUG: Attempt {i+1} to Finish: current_url={final_url}", flush=True)
        return False

    def dismiss_cookies(self):
        print("DEBUG: Checking for cookie modal...", flush=True)
        self.run_js("""
            (function() {
                const btns = Array.from(document.querySelectorAll('button'));
                const accept = btns.find(b => b.innerText && b.innerText.includes('Accept All'));
                if (accept) {
                    accept.click();
                    return "DISMISSED";
                }
                return "NONE";
            })()
        """)
        time.sleep(3)

    def process_item(self, item):
        # Skip logic
        success_bids = {}
        if os.path.exists("data/success_campaigns.txt"):
            with open("data/success_campaigns.txt", "r", encoding='utf-8') as f:
                for line in f:
                    if "|" in line:
                        parts = line.split("|")
                        success_bids[parts[0].strip()] = parts[1].strip()
        
        if item['bid'] in success_bids:
            url = success_bids[item['bid']]
            if "fundraising/start" not in url:
                print(f"DEBUG: Skipping {item['bid']} (Already successful: {url})", flush=True)
                return True
            else:
                print(f"DEBUG: {item['bid']} was previously attempted but URL is just /start. Re-processing...", flush=True)

        print(f"--- Processing {item['bid']} ---", flush=True)
        try:
            # Force navigation to Start to ensure fresh Porto location / category state
            print("DEBUG: Forcing fresh start navigation to https://whydonate.com/fundraising/start...", flush=True)
            self.run_js('window.location.href = "https://whydonate.com/fundraising/start"')
            time.sleep(8)
            
            self.dismiss_cookies()
            time.sleep(2)

            if not self.fill_step1(item): 
                print(f"ERROR: fill_step1 failed for {item['bid']}", flush=True)
                return False
            
            if not self.fill_step2(item): 
                print(f"ERROR: fill_step2 failed for {item['bid']}", flush=True)
                return False
                
            if not self.fill_step3(item): 
                print(f"ERROR: fill_step3 failed for {item['bid']}", flush=True)
                return False
                
            if not self.finalize_campaign(item): 
                print(f"ERROR: finalize_campaign failed for {item['bid']}", flush=True)
                return False
                
            print(f"SUCCESS: Campaign {item['bid']} created and finalized.", flush=True)
            return True
        except Exception as e:
            print(f"ERROR in process_item: {e}", flush=True)
            traceback.print_exc()
            return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python whydonate_batch_automater.py <queue_json>")
        return
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        queue = json.load(f)
    
    automator = WhyDonateAutomator()
    if not automator.connect(): return
    
    for item in queue:
        automator.process_item(item)

if __name__ == "__main__":
    main()
