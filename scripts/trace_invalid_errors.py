import requests
import json
import websocket
import time

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
        
        diag_js = """
        (function() {
            const invalids = Array.from(document.querySelectorAll('.ng-invalid'));
            return invalids.map(el => {
                let errorText = "";
                // Look for nearby mat-error
                const parent = el.closest('mat-form-field') || el.parentElement;
                if (parent) {
                    const errorMsg = parent.querySelector('mat-error, .error-message, .invalid-feedback');
                    if (errorMsg) errorText = errorMsg.innerText.trim();
                }
                return {
                    tag: el.tagName,
                    classes: el.className,
                    id: el.id,
                    error: errorText,
                    placeholder: el.placeholder || "",
                    value: el.value || ""
                };
            });
        })()
        """
        
        print(json.dumps(run_js(ws, diag_js), indent=2))
        ws.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
