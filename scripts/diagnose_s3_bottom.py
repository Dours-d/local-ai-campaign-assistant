import requests
import json
import websocket
import time
import base64

CDP_URL = "http://127.0.0.1:9222/json"

def diagnose():
    try:
        r = requests.get(CDP_URL).json()
        target = next((t for t in r if t['type'] == 'page' and 'whydonate.com' in t.get('url', '')), None)
        if not target: return
        ws = websocket.create_connection(target['webSocketDebuggerUrl'].replace('localhost', '127.0.0.1'))
        
        def run_js(script):
            msg_id = 888
            ws.send(json.dumps({"id": msg_id, "method": "Runtime.evaluate", "params": {"expression": script, "returnByValue": True}}))
            while True:
                res = json.loads(ws.recv())
                if res.get('id') == msg_id: return res['result'].get('result', {}).get('value')

        print("Scrolling to bottom...")
        run_js("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(2)
        
        print("Taking screenshot of bottom...")
        mid = 777
        ws.send(json.dumps({"id": mid, "method": "Page.captureScreenshot"}))
        while True:
            res = json.loads(ws.recv())
            if res.get('id') == mid:
                img_data = base64.b64decode(res['result']['data'])
                with open("data/diagnose_s3_bottom.png", "wb") as f:
                    f.write(img_data)
                print("Screenshot saved to data/diagnose_s3_bottom.png")
                break

        ws.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    diagnose()
