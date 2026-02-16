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
            const btn = document.getElementById('saveStep2') || 
                        document.querySelector('button.mat-stepper-next') ||
                        Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Next'));
            
            const nameInput = document.getElementById('name') || document.querySelector('input[formcontrolname="name"]');
            
            const results = {
                button_found: !!btn,
                button_disabled: btn ? btn.disabled : null,
                button_classes: btn ? btn.className : null,
                button_text: btn ? btn.innerText.trim() : null,
                name_input_found: !!nameInput,
                name_input_value: nameInput ? nameInput.value : null,
                name_input_valid: nameInput ? nameInput.classList.contains('ng-valid') : null,
                name_input_invalid: nameInput ? nameInput.classList.contains('ng-invalid') : null,
                form_invalid: !!document.querySelector('form.ng-invalid'),
                active_step: document.querySelector('mat-step-header[aria-selected="true"]')?.innerText
            };
            return results;
        })()
        """
        
        print(json.dumps(run_js(ws, diag_js), indent=2))
        ws.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
