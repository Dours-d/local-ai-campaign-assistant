import requests
import json
import websocket
import sys

CDP_URL = "http://127.0.0.1:9222/json"

def get_dom():
    r = requests.get(CDP_URL)
    tabs = r.json()
    target_tab = next((t for t in tabs if t.get('type') == 'page' and "whydonate.com" in t.get('url', '')), tabs[0])
    ws = websocket.create_connection(target_tab['webSocketDebuggerUrl'], suppress_origin=True)
    
    msg = {"id": 1, "method": "Runtime.evaluate", "params": {"expression": "document.body.innerHTML", "returnByValue": True}}
    ws.send(json.dumps(msg))
    res = json.loads(ws.recv())
    html = res['result']['result']['value']
    
    with open("data/step2_inner_html.html", "w", encoding='utf-8') as f:
        f.write(html)
    print("Saved to data/step2_inner_html.html")

if __name__ == "__main__":
    get_dom()
