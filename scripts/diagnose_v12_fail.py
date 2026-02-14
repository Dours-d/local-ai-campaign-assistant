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
            msg_id = 1212
            ws.send(json.dumps({"id": msg_id, "method": "Runtime.evaluate", "params": {"expression": script, "returnByValue": True}}))
            while True:
                res = json.loads(ws.recv())
                if res.get('id') == msg_id: return res['result'].get('result', {}).get('value')

        ws.send(json.dumps({"id": 1213, "method": "Log.enable"}))
        ws.send(json.dumps({"id": 1214, "method": "Runtime.enable"}))

        print("Checking Next button state...")
        res = run_js("""
            (function() {
                const btn = document.getElementById('saveBtn');
                return {
                    exists: !!btn,
                    disabled: btn ? btn.disabled : null,
                    text: btn ? btn.innerText : null,
                    classes: btn ? btn.className : null
                };
            })()
        """)
        print(f"Button: {json.dumps(res, indent=2)}")

        print("Scrolling to bottom...")
        run_js("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(2)
        
        print("Taking screenshot...")
        sid = 1215
        ws.send(json.dumps({"id": sid, "method": "Page.captureScreenshot"}))
        while True:
            res = json.loads(ws.recv())
            if res.get('id') == sid:
                with open("data/diagnose_s3_post_v12.png", "wb") as f:
                    f.write(base64.b64decode(res['result']['data']))
                print("Screenshot saved.")
                break

        ws.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    diagnose()
