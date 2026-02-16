
import requests
import json
import websocket
import time

CDP_URL = "http://localhost:9222/json"

def go_to_create():
    r = requests.get(CDP_URL)
    tabs = r.json()
    pages = [t for t in tabs if t.get('type') == 'page']
    target = next((t for t in pages if "whydonate.com" in t.get('url', '')), pages[0])
    ws = websocket.create_connection(target['webSocketDebuggerUrl'], suppress_origin=True)
    ws.send(json.dumps({"id": 1, "method": "Page.navigate", "params": {"url": "https://whydonate.com/fundraising/create"}}))
    ws.close()

if __name__ == "__main__":
    go_to_create()
