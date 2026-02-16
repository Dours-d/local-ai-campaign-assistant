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
            const form = document.querySelector('form');
            if (!form) return "No form found";
            
            const inputs = Array.from(form.querySelectorAll('input, select, textarea, mat-select, mat-slide-toggle, mat-checkbox'));
            const inputStats = inputs.map(i => {
                return {
                    tag: i.tagName,
                    id: i.id,
                    name: i.getAttribute('name') || i.getAttribute('formcontrolname'),
                    placeholder: i.placeholder,
                    value: i.value,
                    type: i.type,
                    classes: i.className,
                    visible: i.offsetWidth > 0,
                    invalid: i.classList.contains('ng-invalid')
                };
            });
            
            const invalidElements = Array.from(form.querySelectorAll('.ng-invalid')).map(el => {
                return {
                    tag: el.tagName,
                    id: el.id,
                    text: el.innerText.trim().substring(0, 50),
                    classes: el.className
                };
            });

            return {
                form_classes: form.className,
                input_stats: inputStats,
                invalid_elements: invalidElements
            };
        })()
        """
        
        print(json.dumps(run_js(ws, diag_js), indent=2))
        ws.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
