import re
import requests
import json
import websocket
import time
import os
import sys
import base64
import traceback

# CDP Utility
CDP_URL = "http://localhost:9222/json"

class WhyDonateAutomator:
    global_msg_id = 100
    def __init__(self, cdp_url=CDP_URL):
        self.cdp_url = cdp_url
        self.ws = None
    
    def connect(self):
        try:
            r = requests.get(self.cdp_url)
            tabs = r.json()
            pages = [t for t in tabs if t.get('type') == 'page']
            if not pages: return False
            target = next((t for t in pages if "whydonate" in t.get('url', '').lower()), pages[0])
            self.ws = websocket.create_connection(target['webSocketDebuggerUrl'], suppress_origin=True)
            self.ws.settimeout(20)
            return True
        except: return False

    def send_cdp(self, method, params=None):
        try:
            WhyDonateAutomator.global_msg_id += 1
            msg = {"id": WhyDonateAutomator.global_msg_id, "method": method, "params": params or {}}
            self.ws.send(json.dumps(msg))
            return WhyDonateAutomator.global_msg_id
        except: return None

    def recv_until_id(self, msg_id, timeout=10):
        if not msg_id: return None
        start = time.time()
        while time.time() - start < timeout:
            try:
                msg = self.ws.recv()
                res = json.loads(msg)
                if res.get('id') == msg_id: return res
            except: continue
        return None

    def run_js(self, js):
        mid = self.send_cdp("Runtime.evaluate", {"expression": js, "returnByValue": True})
        res = self.recv_until_id(mid)
        if res and 'result' in res:
            return res.get('result', {}).get('result', {}).get('value')
        return None

    def click_mouse(self, x, y):
        self.send_cdp("Input.dispatchMouseEvent", {"type": "mousePressed", "x": x, "y": y, "button": "left", "clickCount": 1})
        time.sleep(0.05)
        self.send_cdp("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": x, "y": y, "button": "left", "clickCount": 1})

    def type_string(self, text):
        for char in text:
            self.send_cdp("Input.dispatchKeyEvent", {"type": "char", "text": char})
            time.sleep(0.12)

    def press_key(self, key, code):
        self.send_cdp("Input.dispatchKeyEvent", {"type": "keyDown", "key": key, "windowsVirtualKeyCode": code, "nativeVirtualKeyCode": code})
        self.send_cdp("Input.dispatchKeyEvent", {"type": "keyUp", "key": key, "windowsVirtualKeyCode": code, "nativeVirtualKeyCode": code})

    def capture_screenshot(self, name):
        mid = self.send_cdp("Page.captureScreenshot", {"format": "png"})
        res = self.recv_until_id(mid)
        if res and 'result' in res:
             with open(f"data/debug_{name}.png", "wb") as f:
                f.write(base64.b64decode(res['result']['data']))

    def handle_cookie_consent(self):
        js = """
        (() => {
            const killers = ['reject all', 'accept all', 'agree', 'allow all', 'dismiss', 'bekräfta', 'akzeptieren', 'sluiten', 'close', 'en'];
            document.querySelectorAll('button, a, [role="button"]').forEach(b => {
                const t = (b.innerText || "").toLowerCase();
                if(killers.includes(t) || killers.some(k => t.includes(k) && t.length < 25)) b.click();
            });
            document.querySelectorAll('.cdk-overlay-container, .mat-dialog-container, onc-cookie-consent, cookie-box').forEach(ov => { ov.remove(); });
        })()
        """
        self.run_js(js)

    def get_step(self):
        try:
            url = self.run_js("window.location.href") or ""
            if "/create" not in url: return 0 
            body = (self.run_js("document.body.innerText") or "").lower()
            if "target amount" in body: return 4
            if "fundraiser title" in body: return 3
            if "someone else" in body: return 2
            match = re.search(r"step (\d)[/ ]4", body)
            if match: return int(match.group(1))
        except: pass
        return 1

    def ensure_english(self):
        sel_coords = self.run_js("""
            (() => {
                const sel = document.querySelector('mat-select[formcontrolname="language"]');
                if(sel && !sel.innerText.includes('English') && !sel.innerText.includes('EN')) {
                    sel.scrollIntoView({block:'center'});
                    const r = sel.getBoundingClientRect();
                    return {x: r.x + r.width/2, y: r.y + r.height/2};
                }
                return null;
            })()
        """)
        if sel_coords:
            self.click_mouse(sel_coords['x'], sel_coords['y'])
            time.sleep(2)
            target = self.run_js("""
                (() => {
                    const ops = Array.from(document.querySelectorAll('mat-option'));
                    const en = ops.find(o => o.innerText.includes('English') || o.innerText.includes('EN'));
                    if(en) {
                        const r = en.getBoundingClientRect();
                        return {x: r.x + r.width/2, y: r.y + r.height/2};
                    }
                    return null;
                })()
            """)
            if target: self.click_mouse(target['x'], target['y']); time.sleep(1.5)

    def fill_step1(self, item):
        self.handle_cookie_consent()
        print("Step 1...", flush=True)
        self.ensure_english()
        
        # Category
        self.run_js("""
            const chips = Array.from(document.querySelectorAll('mat-chip, .mat-mdc-chip, .cause-card'));
            const target = chips.find(c => c.innerText.includes('Humanitarian') || c.innerText.includes('Aid')) || chips[0];
            if(target) { target.scrollIntoView({block:'center'}); target.click(); }
        """)
        time.sleep(1)
        
        # Address
        print("DEBUG: Typing Porto...", flush=True)
        focus_coords = self.run_js("""
            (() => {
                const i = document.querySelector('input.location') || document.querySelector('input[id*="mat-input"]') || document.querySelector('input[placeholder*="Location"]');
                if(i) {
                    i.scrollIntoView({block:'center'});
                    i.focus(); i.click(); i.value = '';
                    const r = i.getBoundingClientRect();
                    return {x: r.x + r.width/2, y: r.y + r.height/2};
                }
                return null;
            })()
        """)
        if focus_coords: self.click_mouse(focus_coords['x'], focus_coords['y'])
        
        self.type_string("Porto, Portugal")
        time.sleep(7)
        
        drop_clicked = self.run_js("""
            const item = document.querySelector('.pac-item, .mat-option');
            if(item) { item.click(); true; } else false;
        """)
        if not drop_clicked:
            self.press_key('ArrowDown', 40)
            time.sleep(0.5)
            self.press_key('Enter', 13)
        
        time.sleep(2); self.press_key('Tab', 9); time.sleep(1)
        
        # Click Next
        self.run_js("""
            const btns = Array.from(document.querySelectorAll('button, .mat-raised-button'));
            const b = btns.find(btn => (btn.innerText.toLowerCase().includes('next')) && btn.offsetParent !== null && !btn.className.includes('footer'));
            if(b) { b.scrollIntoView({block:'center'}); b.removeAttribute('disabled'); b.click(); }
        """)
        
        for _ in range(20):
            if self.get_step() >= 2: return True
            time.sleep(0.5)
        self.capture_screenshot("fail_s1")
        return False

    def fill_step2(self, item):
        self.handle_cookie_consent()
        print("Step 2...", flush=True)
        for _ in range(15):
             if self.run_js("document.querySelectorAll('mat-card, .mat-card').length") > 0: break
             time.sleep(1)
        
        self.run_js("""
            const elements = Array.from(document.querySelectorAll('mat-card, .mat-card, [role="radio"]'));
            const t = elements.find(el => el.innerText.includes('Someone Else') || el.innerText.includes('Iemand anders'));
            if(t) { t.scrollIntoView({block:'center'}); t.click(); }
        """)
        time.sleep(2)
        
        name = item.get('beneficiary_name', 'Amir')
        self.run_js(f"const i = document.getElementById('name') || document.querySelector('input[formcontrolname=\"name\"]'); if(i) {{ i.focus(); i.value = {json.dumps(name)}; i.dispatchEvent(new Event('input', {{bubbles:true}})); }}")
        time.sleep(1)
        self.run_js("""
            const btns = Array.from(document.querySelectorAll('button')).find(btn => btn.innerText.toLowerCase().includes('next') && btn.offsetParent !== null);
            if(btns) { btns.scrollIntoView({block:'center'}); btns.click(); }
        """)
        for _ in range(15):
            if self.get_step() >= 3: return True
            time.sleep(0.5)
        return False

    def fill_step3(self, item):
        self.handle_cookie_consent()
        print("Step 3...", flush=True)
        title = item.get('title', 'Support')[:70]
        self.run_js(f"const t = document.querySelector('input[formcontrolname=\"title\"]'); if(t) {{ t.value = {json.dumps(title)}; t.dispatchEvent(new Event('input', {{bubbles:true}})); }}")
        desc = item.get('campaign_description') or "Help."
        self.run_js(f"const e = document.querySelector('.ql-editor'); if(e) {{ e.innerHTML = '<p>' + {json.dumps(desc)} + '</p>'; e.dispatchEvent(new Event('input', {{bubbles:true}})); }}")
        time.sleep(1.5)
        self.run_js("""
            const btns = Array.from(document.querySelectorAll('button')).find(btn => btn.innerText.toLowerCase().includes('next') && btn.offsetParent !== null);
            if(btns) { btns.scrollIntoView({block:'center'}); btns.click(); }
        """)
        for _ in range(12):
            if self.get_step() >= 4: return True
            time.sleep(0.5)
        return False

    def finalize_campaign(self, item):
        print("Finalizing...", flush=True)
        goal = str(item.get('goal', 2500))
        self.run_js(f"const g = document.querySelector('input[formcontrolname=\"target_amount\"]'); if(g) {{ g.value = {json.dumps(goal)}; g.dispatchEvent(new Event('input', {{bubbles:true}})); }}")
        self.run_js("document.querySelectorAll('mat-checkbox').forEach(box => { const input = box.querySelector('input'); if(input && !input.checked) box.click(); });")
        time.sleep(2)
        self.run_js("""
            const btns = Array.from(document.querySelectorAll('button')).find(btn => (btn.innerText.toLowerCase().includes('finish') || btn.innerText.toLowerCase().includes('publish')) && btn.offsetParent !== null);
            if(btns) { btns.scrollIntoView({block:'center'}); btns.removeAttribute('disabled'); btns.click(); }
        """)
        for _ in range(35): 
            time.sleep(1); url = self.run_js("window.location.href")
            if "fundraising/" in url and "/create" not in url:
                print(f"SUCCESS: {url}", flush=True)
                with open("data/success_campaigns.txt", "a") as f: f.write(f"{item['bid']} | {url}\n")
                return True
        return False

    def process_item(self, item):
        if not item.get('bid'): return True 
        if os.path.exists("data/success_campaigns.txt"):
            with open("data/success_campaigns.txt", "r") as f:
                if str(item['bid']) in f.read():
                    print(f"Skipping {item['bid']} (Completed)", flush=True)
                    return True
        print(f"--- Processing {item['bid']} ---", flush=True)
        try:
            self.run_js("window.location.href = 'https://whydonate.com/fundraising/start'")
            time.sleep(10) 
            
            # Handle landing page
            for _ in range(5):
                url = self.run_js("window.location.href") or ""
                if "/create" in url: break
                print("DEBUG: On landing page, clicking Start Fundraiser...", flush=True)
                self.run_js("""
                    const btns = Array.from(document.querySelectorAll('button, a')).filter(b => b.innerText.toLowerCase().includes('start fundraiser'));
                    if(btns.length > 0) btns[0].click();
                """)
                time.sleep(8)
            
            if not self.fill_step1(item): return False
            if not self.fill_step2(item): return False
            if not self.fill_step3(item): return False
            if not self.finalize_campaign(item): return False
            return True
        except Exception as e:
            print(f"Error: {e}", flush=True)
            return False

def main():
    if len(sys.argv) < 2: return
    with open(sys.argv[1], 'r', encoding='utf-8') as f: queue = json.load(f)
    automator = WhyDonateAutomator()
    if not automator.connect(): return
    for item in queue:
        try:
            if not automator.process_item(item):
                time.sleep(5); automator.connect()
        except:
             traceback.print_exc()
             time.sleep(5); automator.connect()

if __name__ == "__main__": main()
