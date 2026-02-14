import requests
import json
import websocket
import time

CDP_URL = "http://127.0.0.1:9222/json"

def diagnose():
    try:
        r = requests.get(CDP_URL).json()
        target = next((t for t in r if t['type'] == 'page' and 'whydonate.com' in t.get('url', '')), None)
        if not target: return
        ws = websocket.create_connection(target['webSocketDebuggerUrl'].replace('localhost', '127.0.0.1'))
        
        def run_js(script):
            msg_id = 1414
            ws.send(json.dumps({"id": msg_id, "method": "Runtime.evaluate", "params": {"expression": script, "returnByValue": True}}))
            while True:
                res = json.loads(ws.recv())
                if res.get('id') == msg_id: return res['result'].get('result', {}).get('value')

        print("Clicking createUploadImageButton...")
        run_js("document.getElementById('createUploadImageButton')?.click()")
        
        for i in range(10):
            time.sleep(1)
            res = run_js("""
                (function() {
                    const next = document.getElementById('saveBtn');
                    const upload = document.getElementById('createUploadImageButton');
                    return {
                        next_disabled: next ? next.disabled : "ERR",
                        upload_text: upload ? upload.innerText : "ERR"
                    };
                })()
            """)
            print(f"Sec {i+1}: {json.dumps(res)}")

        ws.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    diagnose()
