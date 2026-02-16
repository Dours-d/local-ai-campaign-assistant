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
        
        # 1. Type address to trigger dropdown
        js_type = """
        (function() {
            const i = document.querySelector('input.location') || document.querySelector('input[placeholder*="Location"]');
            if (i) {
                i.focus();
                i.value = '';
                i.dispatchEvent(new Event('input', {bubbles:true}));
            }
        })()
        """
        run_js(ws, js_type)
        time.sleep(1)
        
        # Simulate typing "Porto"
        for char in "Porto":
            msg = {"id": 100, "method": "Input.dispatchKeyEvent", "params": {"type": "char", "text": char}}
            ws.send(json.dumps(msg))
            time.sleep(0.1)
        
        time.sleep(3) # Wait for dropdown
        
        # 2. Inspect all elements looking for Porto in a list
        diag_js = """
        (function() {
            const all = Array.from(document.querySelectorAll('*'));
            const matches = all.filter(el => el.innerText && el.innerText.includes('Porto') && el.offsetParent !== null);
            return matches.map(el => {
                return {
                    tag: el.tagName,
                    classes: el.className,
                    text: el.innerText.substring(0, 50),
                    id: el.id
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
