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
            const findInvalid = (el) => {
                if (el.classList.contains('ng-invalid')) {
                    const isInput = ['INPUT', 'SELECT', 'TEXTAREA', 'MAT-SELECT'].includes(el.tagName);
                    if (isInput || el.getAttribute('formcontrolname')) {
                        return {
                            tag: el.tagName,
                            id: el.id,
                            name: el.getAttribute('name') || el.getAttribute('formcontrolname'),
                            placeholder: el.placeholder,
                            classes: el.className,
                            value: el.value,
                            text: el.innerText.trim().substring(0, 50)
                        };
                    }
                }
                let found = [];
                for (let child of el.children) {
                    found = found.concat(findInvalid(child));
                }
                return found;
            };
            
            return {
                all_invalid: findInvalid(document.body),
                form_classes: document.querySelector('form')?.className
            };
        })()
        """
        
        print(json.dumps(run_js(ws, diag_js), indent=2))
        ws.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
