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
            msg_id = 1515
            ws.send(json.dumps({"id": msg_id, "method": "Runtime.evaluate", "params": {"expression": script, "returnByValue": True}}))
            while True:
                res = json.loads(ws.recv())
                if res.get('id') == msg_id: return res['result'].get('result', {}).get('value')

        print("--- Console Logs ---")
        ws.send(json.dumps({"id": 1516, "method": "Runtime.enable"}))
        # Wait a bit for logs to accumulate? No, we need current state.
        
        print("--- Visible Errors ---")
        js_err = """
        (function() {
            const elms = Array.from(document.querySelectorAll('.mat-mdc-form-field-error, .error, [class*="error"], mat-error'));
            return elms.map(el => ({
                text: el.innerText,
                visible: el.offsetParent !== null,
                class: el.className
            }));
        })()
        """
        errs = run_js(js_err)
        print(f"Errors: {json.dumps(errs, indent=2)}")

        print("--- Input Values & Status ---")
        js_vals = """
        (function() {
            const inputs = Array.from(document.querySelectorAll('input, textarea'));
            return inputs.map(i => ({
                id: i.id,
                placeholder: i.placeholder,
                value: i.value,
                valid: i.classList.contains('ng-valid'),
                invalid: i.classList.contains('ng-invalid'),
                touched: i.classList.contains('ng-touched')
            }));
        })()
        """
        vals = run_js(js_vals)
        print(f"Values: {json.dumps(vals, indent=2)}")

        ws.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    diagnose()
