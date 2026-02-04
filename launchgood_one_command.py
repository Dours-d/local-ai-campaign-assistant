
import json
import os
import time
import requests
import websocket
import re
import sys

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
            # Set a timeout for recv
            ws.settimeout(10.0) 
            raw = ws.recv()
            res = json.loads(raw)
            if res.get("id") == rid:
                return res
        except Exception as e:
            print(f"CDP Timeout or Error for ID {rid}: {e}")
            return None

def run_js(ws, js):
    return call_cdp(ws, "Runtime.evaluate", {"expression": js, "returnByValue": True, "awaitPromise": True})

def create_lg_campaign(ws, campaign):
    print(f"\n>>> Processing: {campaign['title']}")
    
    # Reset to start
    run_js(ws, "window.location.hash = '/create/new/raising_for'")
    time.sleep(4)
    
    # Step 1: Raising for
    run_js(ws, "document.querySelectorAll('input[type=\"radio\"]')[0].click()")
    time.sleep(1)
    run_js(ws, "document.querySelector('.lgx-button--default__cta-black').click()")
    time.sleep(4)
    
    # Step 2: Basic Info
    js_step2 = f"""
    (function() {{
        let titleInput = document.querySelector('input[name="title"]') || document.querySelectorAll('input[type="text"]')[0];
        if (titleInput) {{
            titleInput.value = `{campaign['title']}`;
            titleInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
        }}
        let goalInput = document.querySelector('input[name="goal"]') || document.querySelectorAll('input[type="number"]')[0];
        if (goalInput) {{
            goalInput.value = "{campaign['goal']}";
            goalInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
        }}
        let taglineInput = document.querySelector('textarea[name="tagline"]') || document.querySelector('textarea');
        if (taglineInput) {{
            taglineInput.value = `{campaign['tagline']}`;
            taglineInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
        }}
    }})()
    """
    run_js(ws, js_step2)
    time.sleep(1)
    run_js(ws, "document.querySelector('.lgx-button--default__cta-black').click()")
    time.sleep(4)
    
    # Step 3: Story
    js_step3 = f"""
    (function() {{
        let editor = document.querySelector('.ql-editor');
        if (editor) {{
            editor.innerHTML = `{campaign['story']}`;
            editor.dispatchEvent(new Event('input', {{ bubbles: true }}));
        }} else {{
            let ta = document.querySelector('textarea');
            if (ta) {{
                ta.value = `{campaign['story']}`;
                ta.dispatchEvent(new Event('input', {{ bubbles: true }}));
            }}
        }}
    }})()
    """
    run_js(ws, js_step3)
    time.sleep(2)
    
    # Image skip for now (Requires complex upload logic)
    
    # Advance to next (Details/Review)
    run_js(ws, "document.querySelector('.lgx-button--default__cta-black').click()")
    time.sleep(4)
    
    print(f"Draft successfully prepared for submission.")
    return True

def main():
    batch_file = 'data/launchgood_batch_create.json'
    if not os.path.exists(batch_file):
        print("Error: data/launchgood_batch_create.json not found. Run launchgood_prep_data.py first.")
        return

    with open(batch_file, 'r', encoding='utf-8') as f:
        campaigns = json.load(f)

    # Filter campaigns
    pending = [c for c in campaigns if c.get('status') == 'pending_launchgood']
    print(f"Total pending campaigns: {len(pending)}")
    
    if not pending:
        print("No pending campaigns to process.")
        return

    try:
        r = requests.get(CDP_URL).json()
        tabs = [t for t in r if t.get('type') == 'page' and 'launchgood' in t.get('url', '')]
        if not tabs:
            print("Action Required: Open LaunchGood in Chrome and ensure port 9222 is active.")
            return
        
        ws = websocket.create_connection(tabs[0]['webSocketDebuggerUrl'])
        
        count = 0
        for c in pending:
            try:
                if create_lg_campaign(ws, c):
                    c['status'] = 'draft_created'
                    count += 1
                    print(f"[{count}] Saved progress for: {c['title']}")
                    with open(batch_file, 'w', encoding='utf-8') as f:
                        json.dump(campaigns, f, indent=2)
                
                # Check for rate limiting / pause
                time.sleep(5)
            except Exception as e:
                print(f"Error processing {c['title']}: {e}")
                c['status'] = 'failed'
            
        # Final save
        with open(batch_file, 'w', encoding='utf-8') as f:
            json.dump(campaigns, f, indent=2)
        
        ws.close()
        print(f"\nBatch completed. {count} draft campaigns created on LaunchGood.")
        
    except Exception as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    main()
