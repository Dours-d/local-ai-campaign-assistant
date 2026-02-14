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
            msg_id = 1717
            ws.send(json.dumps({"id": msg_id, "method": "Runtime.evaluate", "params": {"expression": script, "returnByValue": True}}))
            while True:
                res = json.loads(ws.recv())
                if res.get('id') == msg_id: return res['result'].get('result', {}).get('value')

        print("--- Upload Section Deep Dive ---")
        js_dive = """
        (function() {
            const inp = document.getElementById('upload_image_input');
            const parent = inp ? inp.closest('div') : null;
            const uploadBtn = document.getElementById('createUploadImageButton');
            
            return {
                inp_html: inp ? inp.outerHTML : "NOT_FOUND",
                parent_html: parent ? parent.outerHTML.substring(0, 1000) : "NOT_FOUND",
                btn_html: uploadBtn ? uploadBtn.outerHTML : "NOT_FOUND",
                btn_disabled: uploadBtn ? uploadBtn.disabled : "ERR"
            };
        })()
        """
        results = run_js(js_dive)
        print(json.dumps(results, indent=2))

        ws.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    diagnose()
