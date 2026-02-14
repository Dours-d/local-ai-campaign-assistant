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
            msg_id = 999
            ws.send(json.dumps({"id": msg_id, "method": "Runtime.evaluate", "params": {"expression": script, "returnByValue": True}}))
            while True:
                res = json.loads(ws.recv())
                if res.get('id') == msg_id: return res['result'].get('result', {}).get('value')

        print("--- Clicking Story Box ---")
        run_js("document.getElementById('createFundraiserStoryDescription')?.click()")
        time.sleep(2)
        
        print("--- DOM After Click ---")
        js_find = """
        (function() {
            const all = Array.from(document.querySelectorAll('textarea, [contenteditable="true"]'));
            return all.map(el => ({
                tag: el.tagName,
                id: el.id,
                class: el.className,
                html: el.outerHTML.substring(0, 100)
            }));
        })()
        """
        results = run_js(js_find)
        print(f"Editable elements after click: {json.dumps(results, indent=2)}")

        ws.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    diagnose()
