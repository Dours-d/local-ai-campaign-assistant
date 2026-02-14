import requests
import json
import websocket
import time

CDP_URL = "http://127.0.0.1:9222/json"

def run():
    try:
        r = requests.get(CDP_URL).json()
        target = next((t for t in r if t['type'] == 'page' and 'whydonate.com' in t.get('url', '')), None)
        if not target:
            print("Target not found")
            return
            
        ws = websocket.create_connection(target['webSocketDebuggerUrl'].replace('localhost', '127.0.0.1'))
        
        def run_js(script):
            msg_id = int(time.time() * 1000)
            ws.send(json.dumps({"id": msg_id, "method": "Runtime.evaluate", "params": {"expression": script, "returnByValue": True}}))
            while True:
                res = json.loads(ws.recv())
                if res.get('id') == msg_id: return res['result'].get('result', {}).get('value')

        print("Current Step:", run_js("document.body.innerText.match(/Step (\\d)\\/4/)?.[1]"))
        
        print(run_js("""
            (function() {
                const b = Array.from(document.querySelectorAll('button')).find(btn => btn.innerText.includes('Next'));
                if (!b) return "NEXT_BTN_NOT_FOUND";
                return "NEXT: " + b.innerText + " | Disabled: " + b.disabled + " | Classes: " + b.className;
            })()
        """))
        
        ws.close()
    except Exception as e: print(e)

if __name__ == "__main__":
    run()
