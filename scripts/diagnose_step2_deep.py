import requests, json, websocket, base64

def diagnose_step2():
    try:
        r = requests.get("http://127.0.0.1:9222/json")
        tabs = r.json()
        target = [t for t in tabs if t.get('type') == 'page' and "whydonate.com" in t.get('url', '')][0]
        ws = websocket.create_connection(target['webSocketDebuggerUrl'])
        
        def run_js(js):
            msg = {"id": 1, "method": "Runtime.evaluate", "params": {"expression": js, "returnByValue": True}}
            ws.send(json.dumps(msg))
            res = json.loads(ws.recv())
            return res.get('result', {}).get('result', {}).get('value')

        print(f"URL: {run_js('window.location.href')}")
        
        # Get all inputs
        inputs = run_js("""
            Array.from(document.querySelectorAll('input, mat-select, mat-radio-button, mat-card')).map(el => ({
                tag: el.tagName,
                type: el.type,
                id: el.id,
                name: el.name,
                placeholder: el.placeholder,
                value: el.value,
                innerText: el.innerText.substring(0, 50),
                classes: el.className,
                rect: el.getBoundingClientRect()
            }))
        """)
        print("Elements found:")
        print(json.dumps(inputs, indent=2))
        
        # Get Next button state
        next_btn = run_js("""
            (function() {
                const btn = document.getElementById('saveStep2') || 
                            document.querySelector('button.mat-stepper-next') ||
                            Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Next'));
                if (btn) {
                    return {
                        id: btn.id,
                        classes: btn.className,
                        disabled: btn.disabled,
                        attributes: Array.from(btn.attributes).map(a => ({name: a.name, value: a.value}))
                    };
                }
                return "NOT_FOUND";
            })()
        """)
        print("Next Button Status:")
        print(json.dumps(next_btn, indent=2))

        ws.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    diagnose_step2()
