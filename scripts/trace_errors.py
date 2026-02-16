import requests
import json
import websocket
import time

CDP_URL = "http://localhost:9222/json"

def run_js(ws, js):
    msg = {"id": 1, "method": "Runtime.evaluate", "params": {"expression": js, "returnByValue": True}}
    ws.send(json.dumps(msg))
    res = json.loads(ws.recv())
    return res.get('result', {}).get('result', {}).get('value')

def main():
    try:
        r = requests.get(CDP_URL).json()
        target = next((t for t in r if 'whydonate.com' in t.get('url', '') and t.get('type') == 'page'), None)
        if not target:
            print("No Whydonate page found")
            return
        
        ws = websocket.create_connection(target['webSocketDebuggerUrl'], suppress_origin=True)
        
        diag_js = """
        (function() {
            const errors = Array.from(document.querySelectorAll('mat-error, .error, .invalid-feedback, .mat-mdc-form-field-error'))
                .map(el => ({
                    tag: el.tagName,
                    text: el.innerText.trim(),
                    visible: el.offsetWidth > 0
                }));
            
            const stepper = document.querySelector('mat-horizontal-stepper');
            const steps = Array.from(document.querySelectorAll('mat-step-header')).map((s, i) => ({
                index: i,
                label: s.innerText.trim(),
                selected: s.getAttribute('aria-selected') === 'true',
                state: s.getAttribute('aria-controls')
            }));

            return {
                errors: errors.filter(e => e.visible),
                steps: steps
            };
        })()
        """
        
        print(json.dumps(run_js(ws, diag_js), indent=2))
        ws.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
