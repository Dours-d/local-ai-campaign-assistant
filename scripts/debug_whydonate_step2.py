import requests
import json
import websocket
import time

CDP_URL = "http://127.0.0.1:9222/json"

def get_socket():
    r = requests.get(CDP_URL).json()
    for t in r:
        if 'whydonate.com' in t.get('url', '') and t['type'] == 'page':
            return websocket.create_connection(t['webSocketDebuggerUrl'])
    return None

def run_js(ws, js):
    msg = json.dumps({
        "id": 1,
        "method": "Runtime.evaluate",
        "params": {"expression": js, "returnByValue": True, "awaitPromise": True}
    })
    ws.send(msg)
    return json.loads(ws.recv())

def main():
    ws = get_socket()
    if not ws:
        print("No Whydonate tab found.")
        return
    
    # Dump text
    res = run_js(ws, "document.body.innerText")
    text = res.get('result', {}).get('result', {}).get('value', 'NO_TEXT')
    print("--- PAGE TEXT START ---")
    print(text)
    print("--- PAGE TEXT END ---")
    
    # Dump buttons
    res_btns = run_js(ws, "Array.from(document.querySelectorAll('button, mat-card, .fundraiser-type-card')).map(b => (b.innerText || '').trim())")
    btns = res_btns.get('result', {}).get('result', {}).get('value', [])
    print(f"Buttons/Cards found: {btns}")
    
    ws.close()

if __name__ == "__main__":
    main()
