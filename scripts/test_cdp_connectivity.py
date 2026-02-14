import requests
import json
import websocket
import time

CDP_URL = "http://127.0.0.1:9222/json"

def test_cdp():
    try:
        r = requests.get(CDP_URL).json()
        target = next((t for t in r if t['type'] == 'page' and 'whydonate.com' in t.get('url', '')), None)
        if not target:
            print("WhyDonate page not found in targets.")
            return
        
        ws_url = target['webSocketDebuggerUrl'].replace('localhost', '127.0.0.1')
        ws = websocket.create_connection(ws_url)
        
        def send(method, params=None):
            msg = {"id": 1, "method": method}
            if params: msg["params"] = params
            ws.send(json.dumps(msg))
            return json.loads(ws.recv())

        print("Enabling Runtime...")
        print(send("Runtime.enable"))
        
        print("Evaluating 'window.location.href'...")
        res = send("Runtime.evaluate", {"expression": "window.location.href", "returnByValue": True})
        print(f"URL: {res.get('result', {}).get('result', {}).get('value')}")
        
        ws.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_cdp()
