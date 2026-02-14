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
        
        def send(method, params=None):
            msg_id = int(time.time() * 1000) % 100000
            msg = {"id": msg_id, "method": method}
            if params: msg["params"] = params
            ws.send(json.dumps(msg))
            start = time.time()
            while time.time() - start < 5:
                res = json.loads(ws.recv())
                if res.get('id') == msg_id: return res
            return None

        def run_js(script):
            res = send("Runtime.evaluate", {"expression": script, "returnByValue": True})
            if res and 'result' in res: return res['result'].get('result', {}).get('value')
            return None

        send("Runtime.enable")
        print(f"URL: {run_js('window.location.href')}")
        
        print("Clicking '.start-card' containing 'Yourself'...")
        res = run_js("""
            (function() {
                const cards = Array.from(document.querySelectorAll('.start-card'));
                const target = cards.find(c => c.innerText.includes('Yourself'));
                if (target) {
                    target.scrollIntoView();
                    target.click();
                    return "CLICKED_CARD";
                }
                return "CARD_NOT_FOUND";
            })()
        """)
        print(f"Selection Click: {res}")
        time.sleep(2)

        print("Checking Next button state...")
        btn = run_js("""
            (function() {
                const b = document.getElementById('saveStep2');
                return b ? { disabled: b.disabled, classes: b.className } : "NOT_FOUND";
            })()
        """)
        print(f"Next Button: {json.dumps(btn, indent=2)}")

        if btn != "NOT_FOUND" and not btn.get('disabled'):
            print("Button enabled! Clicking Next...")
            run_js("document.getElementById('saveStep2').click()")
            time.sleep(5)
            print(f"New URL: {run_js('window.location.href')}")
            print(f"Body segment: {run_js('document.body.innerText.substring(0, 200)')}")

        ws.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    diagnose()
