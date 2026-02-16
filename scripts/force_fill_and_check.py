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
        
        # 1. Ensure we are at Step 2 (assuming already there, but let's try to click Someone Else)
        js_fill = """
        (function() {
            const els = Array.from(document.querySelectorAll('div, span, mat-card-title, .mat-mdc-card-title'));
            const targetS= els.find(el => (el.innerText.includes('Someone Else') || el.innerText.includes('Iemand anders')) && el.offsetParent !== null);
            if (targetS) targetS.click();
            
            const nameInput = document.getElementById('name') || 
                             document.querySelector('input[formcontrolname="name"]') ||
                             document.querySelector('input[placeholder*="Name"]');
            if (nameInput) {
                nameInput.focus();
                nameInput.value = "Diagnostic Test Name";
                nameInput.dispatchEvent(new Event('input', {bubbles:true}));
                nameInput.dispatchEvent(new Event('change', {bubbles:true}));
                nameInput.dispatchEvent(new Event('blur', {bubbles:true}));
            }
            return "Attempted fill";
        })()
        """
        run_js(ws, js_fill)
        time.sleep(2)
        
        # 2. Check errors
        diag_js = """
        (function() {
            const form = document.querySelector('form');
            const invalids = Array.from(document.querySelectorAll('.ng-invalid'));
            return {
                form_classes: form ? form.className : "No Form",
                invalids: invalids.map(el => {
                    return {
                        tag: el.tagName,
                        classes: el.className,
                        id: el.id,
                        placeholder: el.placeholder || "",
                        value: el.value || "",
                        innerText: el.innerText.substring(0, 50)
                    };
                })
            };
        })()
        """
        
        print(json.dumps(run_js(ws, diag_js), indent=2))
        ws.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
