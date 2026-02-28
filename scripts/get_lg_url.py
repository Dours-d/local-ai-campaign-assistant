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

def scrape_url():
    r = requests.get(CDP_URL).json()
    tabs = [t for t in r if t.get('type') == 'page' and 'launchgood' in t.get('url', '')]
    if not tabs:
        print("No Launchgood tab found.")
        return
    
    ws = websocket.create_connection(tabs[0]['webSocketDebuggerUrl'])
    res = run_js(ws, "window.location.href")
    
    val = res.get('result', {}).get('result', {}).get('value', 'Unknown')
    print(f"CURRENT_URL: {val}")
    
    # We want the public campaign string, which is between /campaign/ and /edit
    # Example: https://www.launchgood.com/campaign/global_gaza_resilience_fund_unified_aid_for_300_families#!/campaign/global_gaza_resilience_fund_unified_aid_for_300_families/edit/story
    
    ws.close()

if __name__ == "__main__":
    scrape_url()
