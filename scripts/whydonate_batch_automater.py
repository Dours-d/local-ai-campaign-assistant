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
            # Prefer existing WhyDonate tabs
            target_tab = next((t for t in tabs if "whydonate.com" in t.get('url', '')), tabs[0])
            self.ws = websocket.create_connection(target_tab['webSocketDebuggerUrl'])
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False

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
        mid = self.send_cdp("Runtime.evaluate", {"expression": js, "returnByValue": True})
        res = self.recv_until_id(mid)
        return res.get('result', {}).get('result', {}).get('value')

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
            res = self.run_js("""
                (function() {
                    const el = Array.from(document.querySelectorAll('span, div, p, mat-step-header'))
                        .find(e => e.innerText && e.innerText.match(/Step \\d\\/4/i));
                    if (el) return el.innerText.match(/Step (\\d)\\/4/i)[1];
                    const activeStep = document.querySelector('.mat-step-header[aria-selected="true"] .mat-step-label-active');
                    if (activeStep) return activeStep.innerText.match(/Step (\\d)/i)?.[1];
                    return null;
                })()
            """)
            if res: return int(res)
            res = self.run_js("document.body.innerText.match(/Step (\\d)\\/4/i)?.[1]")
            return int(res) if res else 1
        except: return 1

    def fill_step1(self, item):
        if self.get_step() >= 2:
            print("DEBUG: Already past Step 1. Skipping.", flush=True)
            return True
        print("Processing Step 1/4 (Location Selection)...", flush=True)
        self.take_screenshot(f"data/verify_s1_{item['bid']}.png")
        
        # 1. Select Category (JS)
        print("DEBUG: Selecting Category...", flush=True)
        self.run_js("""
            (function() {
                const target = Array.from(document.querySelectorAll('mat-card, .mat-mdc-card, .category-card, div'))
                    .find(el => el.innerText && el.innerText.trim() === 'Children & Family');
                if (target) {
                    const card = target.closest('mat-card, .mat-mdc-card, .category-card, div[class*="card"]');
                    if (card) card.click(); else target.click();
                    return "CLICKED";
                }
                return "NOT_FOUND";
            })()
        """)
        time.sleep(3)
        
        # 2. Fill Address
        location = "Porto, Portugal"
        print(f"DEBUG: Typing Location: {location}", flush=True)
        self.run_js("""
            const i = document.querySelector('input[formcontrolname="address"], input[placeholder*="address"]');
            if (i) { i.focus(); i.value = ''; i.dispatchEvent(new Event('input', {bubbles:true})); }
        """)
        time.sleep(1)
        self.type_string(location)
        time.sleep(3)
        
        # 3. Select from Dropdown
        print(f"DEBUG: Selecting '{location}' from dropdown...", flush=True)
        drop_res = self.run_js(f"""
            (function() {{
                const options = Array.from(document.querySelectorAll('.pac-item, .mat-option, div[role="option"]'));
                const target = options.find(o => o.innerText.includes({json.dumps(location)}));
                if (target) {{ target.click(); return "CLICKED_TARGET"; }}
                if (options.length > 0) {{ options[0].click(); return "CLICKED_FIRST"; }}
                return "DROPDOWN_EMPTY";
            }})()
        """)
        print(f"DEBUG: Dropdown status: {drop_res}", flush=True)
        time.sleep(3)
        
        # 4. Click Next
        is_enabled = self.run_js("const btn = document.getElementById('saveStep1') || document.querySelector('button.mat-stepper-next'); btn && !btn.disabled")
        if is_enabled:
            print("DEBUG: Next enabled. Clicking...", flush=True)
            self.run_js("const btn = document.getElementById('saveStep1') || document.querySelector('button.mat-stepper-next'); if(btn) btn.click();")
            time.sleep(5)
            if self.get_step() >= 2: return True
        return False

    def fill_step2(self, item):
        if self.get_step() >= 3:
            print("DEBUG: Already past Step 2. Skipping.", flush=True)
            return True
        print(f"DEBUG: fill_step2 start for {item['bid']}", flush=True)
        self.take_screenshot(f"data/verify_s2_start_{item['bid']}.png")
        
        # 1. Select "Someone Else"
        self.run_js("""
            (function() {
                const target = Array.from(document.querySelectorAll('mat-card, .mat-mdc-card, .category-card, div'))
                    .find(el => el.innerText && el.innerText.trim() === 'Someone Else');
                if (target) {
                    const card = target.closest('mat-card, .mat-mdc-card, .category-card, div[class*=\"card\"]');
                    if (card) card.click(); else target.click();
                }
            })()
        """)
        time.sleep(5)
        
        # 2. Fill Beneficiary Name
        raw_name = item['title'].replace("Help ", "").split("&")[0].split("and")[0].split("with")[0].strip()
        name = raw_name[:40].strip()
        print(f"DEBUG: Typing Beneficiary Name: {name}...", flush=True)
        self.run_js("""
            const i = document.querySelector('input[formcontrolname="name"], input[placeholder*="Name"]');
            if (i) { i.focus(); i.value = ''; i.dispatchEvent(new Event('input', {bubbles:true})); }
        """)
        time.sleep(1)
        self.type_string(name)
        time.sleep(3)
        
        # 3. Click Next
        for _ in range(3):
            self.run_js("const btn = document.querySelector('button.mat-stepper-next'); if(btn) btn.click();")
            time.sleep(3)
            if self.get_step() >= 3: return True
        return False

    def fill_step3(self, item):
        if self.get_step() >= 4:
            print("DEBUG: Already past Step 3. Skipping.", flush=True)
            return True
        print("Processing Step 3/4 (Content & Media)...", flush=True)
        self.take_screenshot(f"data/verify_s3_start_{item['bid']}.png")
        
        # 0. Title & Unique URL
        title = item.get('title', 'Help support this campaign')
        from datetime import datetime
        ts = datetime.now().strftime("%H%M%S")
        slug = f"f-{item['bid']}-{ts}"[:70] 
        
        self.run_js(f"""
            (function() {{
                const t = document.querySelector('input[formcontrolname=\"title\"], input.fundraiserTitle');
                if (t) {{ t.focus(); t.value = {json.dumps(title)}; t.dispatchEvent(new Event('input', {{bubbles:true}})); }}
                const u = document.querySelector('input[formcontrolname=\"custom_url\"], input.linkUrl');
                if (u) {{ u.focus(); u.removeAttribute('readonly'); u.value = {json.dumps(slug)}; u.dispatchEvent(new Event('input', {{bubbles:true}})); }}
            }})()
        """)
        time.sleep(2)

        # 1. Fill Story
        description = item.get('campaign_description') or item.get('description') or item.get('story') or "Help support this campaign. We need your support to rebuild lives."
        if len(description) < 15: description += " Please help us support this worthy cause."
        
        print(f"DEBUG: Filling Description ({len(description)} chars)...", flush=True)
        self.run_js("const s = document.getElementById('createFundraiserStoryDescription'); if(s) s.click();")
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
            img_path = os.path.abspath(f"data/temp_{item['bid']}.jpg")
            try:
                r = requests.get(img_url, timeout=10)
                if r.status_code == 200:
                    with open(img_path, 'wb') as f: f.write(r.content)
                    self.upload_file('input[type="file"]', img_path)
                    time.sleep(5)
            except Exception as e: print(f"Image failed: {e}")

        self.take_screenshot(f"data/verify_s3_filled_{item['bid']}.png")
        print("DEBUG: Clicking Next iteratively...", flush=True)
        for i in range(10):
            self.run_js("""
                const nextBtn = Array.from(document.querySelectorAll('button'))
                    .find(b => (b.innerText.includes('Next') || b.classList.contains('mat-stepper-next')) && !b.disabled);
                if (nextBtn) {
                    nextBtn.scrollIntoView({behavior: "smooth", block: "center"});
                    nextBtn.click();
                }
            """)
            time.sleep(4)
            step = self.get_step()
            print(f"DEBUG: Attempt {i+1}, current step: {step}", flush=True)
            if step >= 4:
                print(f"DEBUG: Step 3 advanced after {i+1} attempts.", flush=True)
                return True
            self.take_screenshot(f"data/verify_s3_retry_{i}_{item['bid']}.png")
            
        print(f"WARNING: Step 3 failed for {item['bid']} after 10 attempts.", flush=True)
        return False

    def finalize_campaign(self, item):
        print("Finalizing Campaign (Step 4)...", flush=True)
        goal = str(item.get('goal', 1000))
        self.run_js(f"""
            const g = document.querySelector('input[formcontrolname="target_amount"]');
            if (g) {{ g.focus(); g.value = {json.dumps(goal)}; g.dispatchEvent(new Event('input', {{bubbles:true}})); }}
            document.querySelectorAll('mat-checkbox input').forEach(c => {{ if(!c.checked) c.click(); }});
        """)
        time.sleep(2)
        self.take_screenshot(f"data/verify_s4_{item['bid']}.png")
        
        # Click Finish / Start
        self.run_js("""
            const btns = Array.from(document.querySelectorAll('button'));
            const finish = btns.find(b => b.innerText.includes('Finish') || b.innerText.includes('Start Fundraiser'));
            if (finish) finish.click();
        """)
        time.sleep(10)
        
        final_url = self.get_url()
        if "whydonate.com/fundraising/" in final_url and "/create" not in final_url:
            print(f"SUCCESS: Campaign created at {final_url}", flush=True)
            with open("data/success_campaigns.txt", "a") as f: f.write(f"{item['bid']}|{final_url}\n")
            return True
        return False

    def process_item(self, item):
        print(f"--- Processing {item['bid']} ---", flush=True)
        try:
            url = self.get_url() or ""
            is_creation = "/create" in url or "fundraising/start" in url
            if "whydonate.com" not in url or not is_creation:
                print(f"DEBUG: Navigating to start from {url}...", flush=True)
                self.run_js('window.location.href = "https://whydonate.com/fundraising/start"')
                time.sleep(10)

            if not self.fill_step1(item): return False
            if not self.fill_step2(item): return False
            if not self.fill_step3(item): return False
            if not self.finalize_campaign(item): return False
            return True
        except Exception as e:
            print(f"ERROR: {e}", flush=True)
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
