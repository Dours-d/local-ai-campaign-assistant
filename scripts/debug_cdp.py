import requests
import json
import websocket
import time

CDP_URL = "http://localhost:9222/json"

def main():
    try:
        r = requests.get(CDP_URL)
        tabs = r.json()
        print(f"Tabs: {len(tabs)}")
        for t in tabs:
            print(f"- Type: {t.get('type')}, URL: {t.get('url')}, ID: {t.get('id')}")
        
        pages = [t for t in tabs if t.get('type') == 'page']
        if not pages:
            print("No pages found.")
            return

        target = next((t for t in pages if "whydonate.com" in t.get('url', '')), pages[0])
        print(f"Connecting to: {target['url']}")
        ws = websocket.create_connection(target['webSocketDebuggerUrl'], suppress_origin=True)
        ws.settimeout(3)
        print("Connected.")
        
        # Test simple eval
        msg = {"id": 1, "method": "Runtime.evaluate", "params": {"expression": "document.location.href", "returnByValue": True}}
        ws.send(json.dumps(msg))
        res = json.loads(ws.recv())
        print(f"Eval result: {res}")
        ws.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
