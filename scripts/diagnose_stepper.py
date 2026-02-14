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
            msg_id = 1818
            ws.send(json.dumps({"id": msg_id, "method": "Runtime.evaluate", "params": {"expression": script, "returnByValue": True}}))
            while True:
                res = json.loads(ws.recv())
                if res.get('id') == msg_id: return res['result'].get('result', {}).get('value')

        print("--- Stepper Audit ---")
        js_stepper = """
        (function() {
            const headers = Array.from(document.querySelectorAll('mat-step-header'));
            return headers.map((h, i) => ({
                index: i,
                text: h.innerText,
                selected: h.getAttribute('aria-selected'),
                disabled: h.getAttribute('aria-disabled'),
                html: h.outerHTML.substring(0, 150)
            }));
        })()
        """
        results = run_js(js_stepper)
        print(json.dumps(results, indent=2))

        ws.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    diagnose()
