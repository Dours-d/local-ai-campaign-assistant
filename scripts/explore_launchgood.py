
import requests
import json
import websocket
import time

CDP_URL = "http://localhost:9222/json"

def call_cdp(ws, method, params=None, req_id=1):
    msg = json.dumps({
        "id": req_id,
        "method": method,
        "params": params or {}
    })
    ws.send(msg)
    while True:
        res = json.loads(ws.recv())
        if res.get("id") == req_id:
            return res
        # Ignore events or other responses for now

def explore_launchgood():
    try:
        r = requests.get(CDP_URL).json()
        target_tab = None
        for t in r:
            if t.get('type') == 'page':
                target_tab = t
                break
        
        if not target_tab:
            print("No active Chrome tab found.")
            return

        ws_url = target_tab['webSocketDebuggerUrl']
        ws = websocket.create_connection(ws_url)
        
        start_url = "https://www.launchgood.com/create#!/create/new/raising_for"
        print(f"Navigating to {start_url}...")
        call_cdp(ws, "Page.navigate", {"url": start_url}, req_id=101)
        
        # Wait for actual content to load (SPA might take time)
        time.sleep(8)
        
        js_inspect = """
        (function() {
            let info = {
                url: window.location.href,
                title: document.title,
                visible_text: document.body.innerText.substring(0, 1000).replace(/\\n/g, ' '),
                buttons: Array.from(document.querySelectorAll('button, a.btn, [role="button"]')).map(b => ({
                    text: b.innerText.trim(),
                    tag: b.tagName,
                    classes: b.className
                })).filter(b => b.text),
                inputs: Array.from(document.querySelectorAll('input, select, textarea')).map(i => ({
                    type: i.type,
                    placeholder: i.placeholder,
                    id: i.id,
                    name: i.name,
                    className: i.className
                }))
            };
            return info;
        })()
        """
        print("Evaluating page structure...")
        res = call_cdp(ws, "Runtime.evaluate", {
            "expression": js_inspect,
            "returnByValue": True,
            "awaitPromise": True
        }, req_id=102)
        
        if "result" in res and "value" in res["result"]:
            print(json.dumps(res["result"]["value"], indent=2))
        else:
            print("Failed to get evaluation result:")
            print(json.dumps(res, indent=2))
            
        ws.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    explore_launchgood()
