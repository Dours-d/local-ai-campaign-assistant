import json
import requests
import websocket

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

def scrape_dashboard():
    r = requests.get(CDP_URL).json()
    tabs = [t for t in r if t.get('type') == 'page']
    if not tabs:
        print("No tabs found.")
        return
    
    ws = websocket.create_connection(tabs[0]['webSocketDebuggerUrl'])
    
    title = "Global Gaza Resilience Fund"
    
    js = f"""
    (function() {{
        let links = Array.from(document.querySelectorAll('a'));
        let target = links.find(l => l.innerText.includes('Global Gaza') || l.href.includes('global_gaza_resilience'));
        if (target) {{
            return target.href;
        }}
        return 'Not found';
    }})()
    """
    
    res = run_js(ws, js)
    val = res.get('result', {}).get('result', {}).get('value', 'Unknown')
    print(f"DASHBOARD_EXTRACTED_URL: {val}")
    
    ws.close()

if __name__ == "__main__":
    scrape_dashboard()
