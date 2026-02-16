import requests, json, websocket

def diagnose_toggle():
    try:
        r = requests.get("http://127.0.0.1:9222/json")
        tabs = r.json()
        target = [t for t in tabs if t.get('type') == 'page' and "whydonate.com" in t.get('url', '')][0]
        ws = websocket.create_connection(target['webSocketDebuggerUrl'])
        
        js = """
        (function() {
            const els = Array.from(document.querySelectorAll('*'));
            const label = els.find(el => el.innerText && el.innerText.trim() === 'Set date range');
            if (!label) return {status: "LABEL_NOT_FOUND"};
            
            const row = label.closest('div, mat-list-item, .flex, .mat-mdc-list-item');
            const toggle = row?.querySelector('mat-slide-toggle, mat-checkbox, .mat-mdc-slide-toggle');
            if (!toggle) return {status: "TOGGLE_NOT_FOUND", rowHtml: row?.outerHTML};
            
            return {
                status: "TOGGLE_FOUND",
                tagName: toggle.tagName,
                className: toggle.className,
                ariaChecked: toggle.getAttribute('aria-checked'),
                innerHTML: toggle.innerHTML,
                innerText: toggle.innerText
            };
        })()
        """
        msg = {"id": 1, "method": "Runtime.evaluate", "params": {"expression": js, "returnByValue": True}}
        ws.send(json.dumps(msg))
        res = json.loads(ws.recv())
        result = res.get('result', {}).get('result', {}).get('value')
        print(json.dumps(result, indent=2))
        ws.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    diagnose_toggle()
