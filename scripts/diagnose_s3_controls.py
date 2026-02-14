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
            msg_id = 222
            ws.send(json.dumps({"id": msg_id, "method": "Runtime.evaluate", "params": {"expression": script, "returnByValue": True}}))
            while True:
                res = json.loads(ws.recv())
                if res.get('id') == msg_id: return res['result'].get('result', {}).get('value')

        print("--- Finding Form Controls ---")
        js_find = """
        (function() {
            const all = Array.from(document.querySelectorAll('*'));
            return all.filter(el => el.getAttribute('formcontrolname'))
                      .map(el => ({
                          tag: el.tagName,
                          name: el.getAttribute('formcontrolname'),
                          id: el.id,
                          class: el.className,
                          html: el.outerHTML.substring(0, 100)
                      }));
        })()
        """
        results = run_js(js_find)
        print(f"Form controls found: {json.dumps(results, indent=2)}")

        ws.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    diagnose()
