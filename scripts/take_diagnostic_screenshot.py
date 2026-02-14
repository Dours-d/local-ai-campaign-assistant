import requests
import websocket
import json
import base64
import sys

def take_screenshot(filename="data/diagnostic_screenshot.png"):
    try:
        r = requests.get("http://127.0.0.1:9222/json").json()
        target = next((t for t in r if t['type'] == 'page'), None)
        if not target:
            print("No page target found")
            return False
        
        ws_url = target['webSocketDebuggerUrl'].replace('localhost', '127.0.0.1')
        ws = websocket.create_connection(ws_url, suppress_origin_check=True)
        
        msg = {"id": 1, "method": "Page.captureScreenshot"}
        ws.send(json.dumps(msg))
        
        res = json.loads(ws.recv())
        while 'result' not in res:
            res = json.loads(ws.recv())
            
        data = res['result']['data']
        with open(filename, "wb") as f:
            f.write(base64.b64decode(data))
        
        print(f"Screenshot saved to {filename}")
        ws.close()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    take_screenshot()
