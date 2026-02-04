
import json
import os
import time
import requests
import websocket
import re

CDP_URL = "http://localhost:9222/json"

def call_cdp(ws, method, params=None, req_id=1):
    msg = json.dumps({"id": req_id, "method": method, "params": params or {}})
    ws.send(msg)
    while True:
        res = json.loads(ws.recv())
        if res.get("id") == req_id: return res

def run_js(ws, js):
    return call_cdp(ws, "Runtime.evaluate", {"expression": js, "returnByValue": True, "awaitPromise": True}, req_id=999)

def create_lg_campaign(ws, campaign):
    print(f"--- Creating: {campaign['title']} ---")
    
    # Step 1: Raising for
    run_js(ws, "window.location.hash = '/create/new/raising_for'")
    time.sleep(3)
    
    # Select 'Self/Someone else' (usually the first option)
    run_js(ws, "document.querySelectorAll('input[type=\"radio\"]')[0].click()")
    time.sleep(1)
    run_js(ws, "document.querySelector('.lgx-button--default__cta-black').click()")
    time.sleep(3)
    
    # Step 2: Basic Info (Title, Category, Location)
    # Note: Selectors might need refinement based on actual indices
    js_step2 = f"""
    (function() {{
        let titleInput = document.querySelector('input[name="title"]') || document.querySelectorAll('input[type="text"]')[0];
        if (titleInput) {{
            titleInput.value = "{campaign['title']}";
            titleInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
        }}
        // Goal
        let goalInput = document.querySelector('input[name="goal"]') || document.querySelectorAll('input[type="number"]')[0];
        if (goalInput) {{
            goalInput.value = "{campaign['goal']}";
            goalInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
        }}
        // Tagline
        let taglineInput = document.querySelector('textarea[name="tagline"]') || document.querySelector('textarea');
        if (taglineInput) {{
            taglineInput.value = "{campaign['tagline']}";
            taglineInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
        }}
    }})()
    """
    run_js(ws, js_step2)
    time.sleep(1)
    run_js(ws, "document.querySelector('.lgx-button--default__cta-black').click()")
    time.sleep(3)
    
    # Step 3: Story
    js_step3 = f"""
    (function() {{
        let editor = document.querySelector('.ql-editor') || document.querySelector('textarea');
        if (editor) {{
            editor.innerHTML = `{campaign['story']}`;
            editor.dispatchEvent(new Event('input', {{ bubbles: true }}));
        }}
    }})()
    """
    run_js(ws, js_step3)
    time.sleep(2)
    # Image upload would go here if we can handle the file dialog or JS injection
    # For now, we skip image to get the structure live.
    
    print(f"Form filled for {campaign['title']}. Please review and click Launch.")
    return True

def main():
    batch_file = 'data/launchgood_batch_create.json'
    if not os.path.exists(batch_file):
        print("Data file not found.")
        return

    with open(batch_file, 'r', encoding='utf-8') as f:
        campaigns = json.load(f)

    r = requests.get(CDP_URL).json()
    tabs = [t for t in r if t.get('type') == 'page' and 'launchgood' in t.get('url', '')]
    if not tabs:
        print("Please open LaunchGood start page in Chrome (port 9222)")
        return
    
    ws = websocket.create_connection(tabs[0]['webSocketDebuggerUrl'])
    
    # Process all pending campaigns
    to_process = [c for c in campaigns if c.get('status') == 'pending_launchgood']
    
    for c in to_process:
        success = create_lg_campaign(ws, c)
        if success:
            c['status'] = 'draft_created'
            time.sleep(5)
            
    # Save progress
    with open(batch_file, 'w', encoding='utf-8') as f:
        json.dump(campaigns, f, indent=2)
    
    ws.close()

if __name__ == "__main__":
    main()
