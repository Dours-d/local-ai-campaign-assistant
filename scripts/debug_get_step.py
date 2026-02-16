import requests
import json
import websocket

CDP_URL = "http://localhost:9222/json"

def run_js(ws, js):
    msg = {"id": 1, "method": "Runtime.evaluate", "params": {"expression": js, "returnByValue": True}}
    ws.send(json.dumps(msg))
    while True:
        res = json.loads(ws.recv())
        if res.get('id') == 1:
            return res.get('result', {}).get('result', {}).get('value')

def main():
    try:
        r = requests.get(CDP_URL).json()
        target = next((t for t in r if 'whydonate.com' in t.get('url', '') and t.get('type') == 'page'), None)
        if not target:
            print("No Whydonate page found")
            return
        
        ws = websocket.create_connection(target['webSocketDebuggerUrl'], suppress_origin=True)
        
        js = """
        (function() {
            const step_active = (function() {
                const header = document.querySelector('mat-step-header[aria-selected="true"]')?.innerText;
                if (header) return header;
                const els = Array.from(document.querySelectorAll('div, span, p, h1, h2, h3, b, strong'));
                const stepFloater = els.find(el => el.innerText && /Step \\d\\/4/.test(el.innerText) && el.offsetParent !== null);
                return stepFloater ? stepFloater.innerText : "NOT_FOUND";
            })();
            return step_active;
        })()
        """
        print(f"Step Active Result: {run_js(ws, js)}")
        ws.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
