import json
import requests
import websocket
import time

CDP_URL = "http://127.0.0.1:9222/json"

def diagnose_step2():
    try:
        r = requests.get(CDP_URL)
        tabs = r.json()
        target_tab = next((t for t in tabs if "whydonate.com" in t.get('url', '')), tabs[0])
        ws = websocket.create_connection(target_tab['webSocketDebuggerUrl'])
        
        def run_js(js):
            msg = {"id": 1, "method": "Runtime.evaluate", "params": {"expression": js, "returnByValue": True}}
            ws.send(json.dumps(msg))
            res = json.loads(ws.recv())
            return res.get('result', {}).get('result', {}).get('value')

        print(f"URL: {run_js('window.location.href')}")
        print(f"Step: {run_js('document.body.innerText').count('Step')}")
        
        # Check for "Someone Else" and "Yourself" cards
        cards = run_js("""
            Array.from(document.querySelectorAll('mat-card, .mat-mdc-card, .category-card')).map(c => ({
                text: c.innerText.trim(),
                visible: c.getBoundingClientRect().height > 0
            }))
        """)
        print(f"Cards: {json.dumps(cards, indent=2)}")
        
        # Check for inputs
        inputs = run_js("""
            Array.from(document.querySelectorAll('input')).map(i => ({
                formcontrolname: i.getAttribute('formcontrolname'),
                placeholder: i.getAttribute('placeholder'),
                value: i.value,
                visible: i.getBoundingClientRect().height > 0
            }))
        """)
        print(f"Inputs: {json.dumps(inputs, indent=2)}")
        
        # Check for buttons
        buttons = run_js("""
            Array.from(document.querySelectorAll('button')).map(b => ({
                text: b.innerText.trim(),
                disabled: b.disabled,
                visible: b.getBoundingClientRect().height > 0
            }))
        """)
        print(f"Buttons: {json.dumps(buttons, indent=2)}")
        
        ws.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    diagnose_step2()
