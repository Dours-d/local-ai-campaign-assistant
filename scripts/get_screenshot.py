import json
import requests
import websocket
import base64

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

def capture_screenshot():
    r = requests.get(CDP_URL).json()
    tabs = [t for t in r if t.get('type') == 'page']
    if not tabs:
        print("No tabs found.")
        return
    
    ws = websocket.create_connection(tabs[0]['webSocketDebuggerUrl'])
    
    res = call_cdp(ws, "Page.captureScreenshot", {"format": "png"})
    if res and res.get('result', {}).get('data'):
        data = res['result']['data']
        with open("launchgood_screenshot.png", "wb") as f:
            f.write(base64.b64decode(data))
        print("Screenshot saved to launchgood_screenshot.png")
    else:
        print("Screenshot failed.")
        
    ws.close()

if __name__ == "__main__":
    capture_screenshot()
