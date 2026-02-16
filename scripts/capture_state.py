
import requests
import json
import websocket
import base64

CDP_URL = "http://localhost:9222/json"

def get_screenshot():
    r = requests.get(CDP_URL)
    tabs = r.json()
    pages = [t for t in tabs if t.get('type') == 'page']
    target = next((t for t in pages if "whydonate.com" in t.get('url', '')), pages[0])
    ws = websocket.create_connection(target['webSocketDebuggerUrl'], suppress_origin=True)
    msg = {"id": 1, "method": "Page.captureScreenshot", "params": {"format": "png"}}
    ws.send(json.dumps(msg))
    while True:
        res = json.loads(ws.recv())
        if res.get('id') == 1:
            with open("data/debug_current_state.png", "wb") as f:
                f.write(base64.b64decode(res['result']['data']))
            break
    ws.close()

if __name__ == "__main__":
    try: get_screenshot(); print("Screenshot saved to data/debug_current_state.png")
    except Exception as e: print(e)
