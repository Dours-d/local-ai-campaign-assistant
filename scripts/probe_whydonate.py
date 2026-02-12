import requests
import json
import websocket
import time
import os

CDP_URL = "http://127.0.0.1:9222/json"

def run_js(ws, js, timeout=10):
    msg_id = 9999
    msg = json.dumps({
        "id": msg_id,
        "method": "Runtime.evaluate",
        "params": { "expression": js, "returnByValue": True }
    })
    ws.send(msg)
    start_t = time.time()
    while time.time() - start_t < timeout:
        try:
            ws.settimeout(1)
            raw = ws.recv()
            res = json.loads(raw)
            if res.get('id') == msg_id: return res.get('result', {}).get('result', {}).get('value')
        except: continue
    return "Timeout"

def probe():
    try:
        tabs = requests.get(CDP_URL).json()
        target = [t for t in tabs if 'whydonate.com' in t.get('url', '') and t['type'] == 'page'][0]
        ws = websocket.create_connection(
            target['webSocketDebuggerUrl'].replace('localhost', '127.0.0.1'),
            suppress_origin_check=True,
            header={"Host": "127.0.0.1:9222"}
        )
        
        print("Checking for existing Raneen campaigns...")
        js = "Array.from(document.querySelectorAll('*')).some(el => el.innerText && el.innerText.includes('Raneen'))"
        found = run_js(ws, js)
        print(f"Found 'Raneen' on page: {found}")
        
        js_list = "Array.from(document.querySelectorAll('a')).map(a => ({text: a.innerText, href: a.href})).filter(o => o.text.includes('Raneen'))"
        matches = run_js(ws, js_list)
        print(f"Matching links: {matches}")
        
        ws.close()
    except Exception as e: print(f"Error: {e}")

if __name__ == "__main__":
    probe()
