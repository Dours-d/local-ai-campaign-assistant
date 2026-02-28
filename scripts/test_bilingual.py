import json
import time
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
    # Fix returnByValue being unreliable for deep DOM elements
    res = call_cdp(ws, "Runtime.evaluate", {"expression": js, "returnByValue": False, "awaitPromise": True})
    return res

def test_dunya_bilingual():
    r = requests.get(CDP_URL).json()
    tabs = [t for t in r if t.get('type') == 'page']
    if not tabs:
        print("No tabs.")
        return
    ws = websocket.create_connection(tabs[0]['webSocketDebuggerUrl'])
    
    print("Navigating to local Dunya portal...")
    run_js(ws, "window.location.href = 'http://127.0.0.1:5010/brain'")
    time.sleep(3)
    
    # Test Arabic
    print("Clicking Arabic Toggle...")
    js_ar = "document.querySelector('button[onclick=\"setLanguage(\\'ar\\')\"]').click(); Array.from(document.querySelectorAll('[data-i18n]')).slice(0,3).map(el => el.innerText).join(' | ');"
    res_ar = call_cdp(ws, "Runtime.evaluate", {"expression": js_ar, "returnByValue": True})
    print(f"Arabic Text Rendered: {res_ar.get('result', {}).get('result', {}).get('value')}")
    
    time.sleep(1)
    
    # Test English
    print("Clicking English Toggle...")
    js_en = "document.querySelector('button[onclick=\"setLanguage(\\'en\\')\"]').click(); Array.from(document.querySelectorAll('[data-i18n]')).slice(0,3).map(el => el.innerText).join(' | ');"
    res_en = call_cdp(ws, "Runtime.evaluate", {"expression": js_en, "returnByValue": True})
    print(f"English Text Rendered: {res_en.get('result', {}).get('result', {}).get('value')}")
    
    ws.close()

if __name__ == "__main__":
    test_dunya_bilingual()
