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
            msg_id = 123
            ws.send(json.dumps({"id": msg_id, "method": "Runtime.evaluate", "params": {"expression": script, "returnByValue": True}}))
            while True:
                res = json.loads(ws.recv())
                if res.get('id') == msg_id: return res['result'].get('result', {}).get('value')

        print("--- Step 3 Details ---")
        js_dump = """
        (function() {
            const inputs = Array.from(document.querySelectorAll('input, textarea, [contenteditable="true"]'));
            return inputs.map(i => ({
                tag: i.tagName,
                type: i.getAttribute('type'),
                placeholder: i.getAttribute('placeholder') || i.getAttribute('aria-label'),
                id: i.id,
                name: i.getAttribute('name'),
                val: i.value || i.innerText
            }));
        })()
        """
        results = run_js(js_dump)
        print(f"Inputs found: {json.dumps(results, indent=2)}")

        ws.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    diagnose()
