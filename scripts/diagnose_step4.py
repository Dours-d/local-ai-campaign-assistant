import requests, json, websocket, base64

def diagnose_step4():
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
        
        # Get all text
        # print(f"Body Text: {run_js('document.body.innerText')}")
        
        # Get all buttons
        buttons = run_js("""
            Array.from(document.querySelectorAll('button')).map(b => ({
                text: b.innerText.trim(),
                disabled: b.disabled,
                classes: b.className,
                id: b.id
            }))
        """)
        print("Buttons:")
        print(json.dumps(buttons, indent=2))
        
        # Get all checkboxes
        checkboxes = run_js("""
            Array.from(document.querySelectorAll('mat-checkbox, input[type="checkbox"]')).map(c => ({
                text: c.innerText.trim(),
                checked: c.querySelector('input')?.checked || c.checked,
                visible: c.getBoundingClientRect().height > 0
            }))
        """)
        print("Checkboxes:")
        print(json.dumps(checkboxes, indent=2))
        
        # Get all toggles
        toggles = run_js("""
            Array.from(document.querySelectorAll('mat-slide-toggle')).map(t => ({
                text: t.innerText.trim(),
                checked: t.classList.contains('mat-checked') || t.querySelector('input')?.checked,
                visible: t.getBoundingClientRect().height > 0
            }))
        """)
        print("Toggles:")
        print(json.dumps(toggles, indent=2))

        # Full DOM dump for analysis
        html = run_js("document.documentElement.outerHTML")
        with open("data/step4_debug.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("DOM dump saved to data/step4_debug.html")

        # Take multiple screenshots (scrolling down)
        ws.send(json.dumps({'id': 10, 'method': 'Page.captureScreenshot'}))
        res = json.loads(ws.recv())
        with open("data/step4_top.png", "wb") as f:
            f.write(base64.b64decode(res['result']['data']))
            
        run_js("window.scrollTo(0, document.body.scrollHeight)")
        ws.send(json.dumps({'id': 11, 'method': 'Page.captureScreenshot'}))
        res = json.loads(ws.recv())
        with open("data/step4_bottom.png", "wb") as f:
            f.write(base64.b64decode(res['result']['data']))
        print("Screenshots saved.")

        ws.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    diagnose_step4()
