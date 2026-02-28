import json
import time
import requests
import websocket
import os

CDP_URL = "http://localhost:9222/json"

_req_id = 0
def get_next_id():
    global _req_id
    _req_id += 1
    return _req_id

def call_cdp(ws, method, params=None):
    rid = get_next_id()
    msg = json.dumps({"id": rid, "method": method, "params": params or {}})
    ws.send(msg)
    while True:
        try:
            ws.settimeout(10.0) 
            raw = ws.recv()
            res = json.loads(raw)
            if res.get("id") == rid:
                return res
        except Exception:
            return None

def run_js(ws, js):
    return call_cdp(ws, "Runtime.evaluate", {"expression": js, "returnByValue": True, "awaitPromise": True})

def create_umbrella_fund():
    r = requests.get(CDP_URL).json()
    tabs = [t for t in r if t.get('type') == 'page' and 'launchgood' in t.get('url', '')]
    if not tabs:
        print("No LaunchGood tab found.")
        return
    
    ws = websocket.create_connection(tabs[0]['webSocketDebuggerUrl'])
    
    # 1. Force navigation to the new campaign creation exact route
    print("Navigating to creation page...")
    run_js(ws, "window.location.href = 'https://www.launchgood.com/create#!/create/new/raising_for'")
    time.sleep(6) # wait for SPA load
    
    print("Clicking 'Myself or someone else' and Next...")
    # Completely foolproof dom traversal to find element by exact text
    js_click_first = """
    (function() {
        function triggerClick(el) {
            el.click();
            el.dispatchEvent(new MouseEvent('mousedown', {bubbles: true}));
            el.dispatchEvent(new MouseEvent('mouseup', {bubbles: true}));
        }
        
        let allNodes = Array.from(document.querySelectorAll('*'));
        let targetNode = allNodes.find(n => n.innerText && n.innerText.trim() === 'Myself or someone else');
        
        if (targetNode) {
            // Traverse up to find a button-like or actionable container
            let clickable = targetNode.closest('div') || targetNode.parentElement;
            triggerClick(clickable);
            return "Found and clicked 'Myself or someone else'";
        } else {
             // Fallback to generic cards
             let generic = Array.from(document.querySelectorAll('div')).find(div => div.innerText && div.innerText.includes('personal bank account') && div.innerText.includes('Myself or someone else'));
             if (generic) { triggerClick(generic); return "Clicked fallback container"; }
        }
        return "Failed to find 'Myself or someone else'";
    })();
    """
    run_js(ws, js_click_first)
    time.sleep(2)
    
    # Target the generic Next button that has the text 'Next' exactly
    js_click_next = """
    (function() {
        let buttons = Array.from(document.querySelectorAll('button, a, div[role="button"]'));
        let nextBtn = buttons.find(b => b.innerText && b.innerText.trim().startsWith('Next'));
        if (nextBtn) { 
            nextBtn.click();
            nextBtn.dispatchEvent(new MouseEvent('mousedown', {bubbles: true}));
            nextBtn.dispatchEvent(new MouseEvent('mouseup', {bubbles: true}));
        }
    })();
    """
    run_js(ws, js_click_next)
    time.sleep(5)
    
    print("Filling Basic Info...")
    title = "Global Gaza Resilience Fund: Unified Aid for 300+ Families"
    tagline = "A transparent, collective fund preserving the dignity of 302 families in Gaza."
    goal = "1500000"
    
    js_step2 = f"""
    (function() {{
        let titleInput = document.querySelector('input[name="title"]') || document.querySelectorAll('input[type="text"]')[0];
        if (titleInput) {{
            titleInput.value = `{title}`;
            titleInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
        }}
        let goalInput = document.querySelector('input[name="goal"]') || document.querySelectorAll('input[type="number"]')[0];
        if (goalInput) {{
            goalInput.value = "{goal}";
            goalInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
        }}
        let taglineInput = document.querySelector('textarea[name="tagline"]') || document.querySelector('textarea');
        if (taglineInput) {{
            taglineInput.value = `{tagline}`;
            taglineInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
        }}
    }})()
    """
    run_js(ws, js_step2)
    time.sleep(2)
    run_js(ws, "let btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Next') || b.innerText.includes('Continue')); if(btn) btn.click(); else document.querySelector('.lgx-button--default__cta-black')?.click();")
    time.sleep(6)
    
    print("Filling Story...")
    story = "<h2>Standing with the Families of Gaza</h2><p>This is a collective fund supporting over 300 families...</p>"
    js_step3 = f"""
    (function() {{
        let editor = document.querySelector('.ql-editor');
        if (editor) {{
            editor.innerHTML = `{story}`;
            editor.dispatchEvent(new Event('input', {{ bubbles: true }}));
        }}
    }})()
    """
    run_js(ws, js_step3)
    time.sleep(2)
    run_js(ws, "document.querySelector('.lgx-button--default__cta-black')?.click()")
    time.sleep(4)
    
    print("Printing active URL to identify successful draft creation...")
    res = run_js(ws, "window.location.href")
    val = res.get('result', {}).get('result', {}).get('value', 'Unknown')
    print(f"Final URL: {val}")
    with open('lg_url.txt', 'w') as f:
        f.write(val)
        
    ws.close()

if __name__ == "__main__":
    create_umbrella_fund()
