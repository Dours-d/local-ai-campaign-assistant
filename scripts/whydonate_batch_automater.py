import requests
import json
import websocket
import time
import os
import sys

CDP_URL = "http://127.0.0.1:9222/json"

class WhyDonateAutomator:
    def __init__(self, cdp_url=CDP_URL):
        self.cdp_url = cdp_url
        self.ws = None

    def connect(self):
        try:
            r = requests.get(self.cdp_url).json()
            target = next((t for t in r if t['type'] == 'page'), None)
            if not target: return False
            self.ws = websocket.create_connection(
                target['webSocketDebuggerUrl'].replace('localhost', '127.0.0.1'),
                suppress_origin_check=True,
                header={"Host": "127.0.0.1:9222"}
            )
            self.send_cdp("Runtime.enable")
            self.send_cdp("DOM.enable")
            return True
        except: return False

    def send_cdp(self, method, params=None):
        msg_id = int(time.time() * 1000) % 1000000
        msg = {"id": msg_id, "method": method}
        if params: msg["params"] = params
        self.ws.send(json.dumps(msg))
        return msg_id

    def recv_until_id(self, msg_id, timeout=10):
        start = time.time()
        while time.time() - start < timeout:
            try:
                self.ws.settimeout(0.5)
                res = json.loads(self.ws.recv())
                if res.get('id') == msg_id: return res
            except: continue
        return None

    def run_js(self, js):
        mid = self.send_cdp("Runtime.evaluate", {"expression": js, "returnByValue": True, "awaitPromise": True})
        res = self.recv_until_id(mid)
        if res and 'result' in res:
            return res['result'].get('result', {}).get('value')
        return None

    def take_screenshot(self, filename, scroll_to_bottom=False):
        if scroll_to_bottom:
            self.run_js("window.scrollTo(0, document.body.scrollHeight)")
        else:
            self.run_js("window.scrollTo(0, 0)")
        time.sleep(1)
        mid = self.send_cdp("Page.captureScreenshot")
        res = self.recv_until_id(mid, timeout=15)
        if res and 'result' in res:
            import base64
            with open(filename, "wb") as f:
                f.write(base64.b64decode(res['result']['data']))
            print(f"Screenshot saved to {filename}")
            return True
        return False

    def click_text(self, text, selector="button, span, div, a"):
        js = f"""
        (function() {{
            const elms = Array.from(document.querySelectorAll('{selector}'));
            const target = elms.find(el => (el.innerText || "").includes("{text}"));
            if (target) {{
                target.scrollIntoView();
                target.click();
                return true;
            }}
            return false;
        }})()
        """
        return self.run_js(js)

    def type_text(self, text):
        for char in text:
            # Use only 'char' event to avoid doubling in some browser environments
            self.send_cdp("Input.dispatchKeyEvent", {"type": "char", "text": char})
            time.sleep(0.05)

    def get_step(self):
        return self.run_js("document.body.innerText.match(/Step (\\d)\\/4/)?.[1]")

    def upload_image(self, file_path):
        try:
            mid = self.send_cdp("DOM.getDocument")
            root = self.recv_until_id(mid)['result']['root']
            mid = self.send_cdp("DOM.querySelector", {"nodeId": root['nodeId'], "selector": "input[type='file']"})
            node_res = self.recv_until_id(mid)
            if not node_res or 'result' not in node_res: return False
            node_id = node_res['result']['nodeId']
            mid = self.send_cdp("DOM.setFileInputFiles", {"files": [file_path], "nodeId": node_id})
            return True
        except: return False

    def close(self):
        if self.ws: self.ws.close()

def process_batch(queue_file):
    if not os.path.exists(queue_file):
        print("Queue file not found.")
        return

    with open(queue_file, 'r', encoding='utf-8') as f:
        queue = json.load(f)

    for item in queue:
        print(f"\n--- Starting {item['bid']} ---")
        automator = WhyDonateAutomator()
        if not automator.connect():
            print("Failed to connect.")
            continue

        try:
            # 0. Load Page
            automator.run_js("window.location.href = 'https://whydonate.com/fundraising/start'")
            time.sleep(10)
            
            # 1. Step 1: Category & Address
            print("Processing Step 1/4...")
            automator.take_screenshot(f"data/verify_s1_{item['bid']}.png")
            
            # Fill address - focus and type
            js_focus = """
            (function() {
                const addr = document.querySelector('input[formcontrolname="location"]');
                if (addr) {
                    addr.focus();
                    addr.scrollIntoView();
                    return true;
                }
                return false;
            })()
            """
            focused = automator.run_js(js_focus)
            print(f"Focused address: {focused}")
            if focused:
                automator.type_text("Amman, Jordan")
                time.sleep(4) 
                
                # Try to click the first suggestion
                js_select = """
                (function() {
                    const selectors = [
                        'mat-option', 
                        '.mdc-list-item', 
                        '.pac-item', 
                        '.autocomplete-result',
                        '.mat-mdc-autocomplete-panel .mdc-list-item'
                    ];
                    for (const s of selectors) {
                        const opt = document.querySelector(s);
                        if (opt && opt.offsetParent !== null) {
                            opt.scrollIntoView();
                            opt.click();
                            return "Clicked " + s;
                        }
                    }
                    return "No suggestion found";
                })()
                """
                res = automator.run_js(js_select)
                print(f"Selection Result: {res}")
                
                # If no matching suggestion found by selector, try Enter as fallback
                if "No suggestion" in str(res):
                    print("Falling back to Enter key...")
                    automator.send_cdp("Input.dispatchKeyEvent", {"type": "keyDown", "windowsVirtualKeyCode": 13, "nativeVirtualKeyCode": 13})
                    automator.send_cdp("Input.dispatchKeyEvent", {"type": "keyUp", "windowsVirtualKeyCode": 13, "nativeVirtualKeyCode": 13})
                
                time.sleep(2)
                automator.take_screenshot(f"data/s1_addr_final_{item['bid']}.png")
            
            # Click Category and verify
            print("Clicking Humanitarian Aid...")
            automator.click_text("Humanitarian Aid")
            time.sleep(2)
            
            chip_state = automator.run_js("JSON.stringify(Array.from(document.querySelectorAll('mat-chip-row, .mdc-chip')).filter(el => el.innerText.includes('Humanitarian Aid')).map(el => ({cls: el.className})))")
            print(f"Chip State: {chip_state}")
            
            automator.take_screenshot(f"data/s1_cat_clicked_{item['bid']}.png", scroll_to_bottom=False)
            
            # Click Next
            print("Clicking Next...")
            automator.click_text("Next", "button")
            time.sleep(5)
            automator.take_screenshot(f"data/s1_after_next_{item['bid']}.png", scroll_to_bottom=True)
            
            # 2. Step 2: Target
            if automator.get_step() != "2":
                print(f"Warning: Expected Step 2, but at Step {automator.get_step()}. Retrying Next...")
                automator.click_text("Next", "button")
                time.sleep(3)
            
            print("Processing Step 2/4...")
            automator.take_screenshot(f"data/verify_s2_{item['bid']}.png")
            automator.click_text("Myself")
            time.sleep(2)
            automator.click_text("Next", "button")
            time.sleep(5)

            # 3. Step 3: Details
            if automator.get_step() != "3":
                print(f"Warning: Expected Step 3, but at Step {automator.get_step()}. Retrying Next...")
                automator.click_text("Next", "button")
                time.sleep(3)

            print("Processing Step 3/4...")
            automator.take_screenshot(f"data/verify_s3_{item['bid']}.png")
            
            policy = f"\n\n---\n**Beneficiary ID: {item['bid']}**\nFunds are disbursed when €100 is reached."
            desc = item['description'] + policy
            
            js_fill = f"""
            (function() {{
                const title = document.querySelector('input[placeholder*="Title"]');
                if (title) {{ title.value = {json.dumps(item['title'])}; title.dispatchEvent(new Event('input', {{bubbles:true}})); }}
                const story = document.querySelector('textarea');
                if (story) {{ story.value = {json.dumps(desc)}; story.dispatchEvent(new Event('input', {{bubbles:true}})); }}
                const goal = document.querySelector('input[type="number"]');
                if (goal) {{ goal.value = "{item['goal']}"; goal.dispatchEvent(new Event('input', {{bubbles:true}})); }}
            }})()
            """
            automator.run_js(js_fill)
            automator.upload_image(item['image'])
            time.sleep(8)
            
            automator.click_text("Next", "button")
            time.sleep(5)

            # 4. Step 4: Finalize
            if automator.get_step() != "4":
                print(f"Warning: Expected Step 4, but at Step {automator.get_step()}.")
            
            print("Processing Step 4/4...")
            automator.take_screenshot(f"data/verify_s4_{item['bid']}.png")
            
            # Accept terms
            automator.run_js("document.querySelectorAll('mat-checkbox').forEach(c => c.click())")
            time.sleep(2)
            
            # Click Final Finish (STRICT button only)
            automator.click_text("Finish", "button.mat-flat-button, button.mat-raised-button")
            time.sleep(15)
            
            automator.take_screenshot(f"data/verify_final_{item['bid']}.png")
            print(f"Done. Final URL: {automator.run_js('window.location.href')}")

        except Exception as e:
            print(f"System Error: {e}")
        finally:
            automator.close()

if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else "data/batch_queue.json"
    process_batch(q)
