
import requests
import json
import websocket
import time

CDP_URL = "http://localhost:9222/json"

def call_cdp(ws, method, params=None, req_id=1):
    msg = json.dumps({"id": req_id, "method": method, "params": params or {}})
    ws.send(msg)
    while True:
        res = json.loads(ws.recv())
        if res.get("id") == req_id: return res

def run_js(ws, js):
    return call_cdp(ws, "Runtime.evaluate", {"expression": js, "returnByValue": True, "awaitPromise": True}, req_id=400)

def capture_step3():
    try:
        r = requests.get(CDP_URL).json()
        ws_url = [t['webSocketDebuggerUrl'] for t in r if t.get('type') == 'page' and 'launchgood' in t.get('url', '')][0]
        ws = websocket.create_connection(ws_url)
        
        print("Waiting to be on Step 3...")
        # We assume the last run left us on Step 3 for the last campaign
        
        js = """
        (function() {
            let inputs = Array.from(document.querySelectorAll('input, [role="button"], .ql-editor')).map(el => ({
                tag: el.tagName,
                type: el.type || '',
                id: el.id,
                classes: el.className,
                text: el.innerText || el.value || ''
            }));
            return {
                html: document.body.innerHTML.substring(0, 100000),
                inputs: inputs
            };
        })()
        """
        res = run_js(ws, js)
        data = res["result"]["value"]
        with open("launchgood_step3.json", "w", encoding='utf-8') as f:
            json.dump(data["inputs"], f, indent=2)
        print("Captured Step 3 info.")
        ws.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    capture_step3()
