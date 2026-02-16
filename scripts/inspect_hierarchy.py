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
            const els = Array.from(document.querySelectorAll('*'));
            const target = els.find(el => el.innerText && el.innerText.trim() === 'Someone Else');
            if (!target) return "Someone Else not found";
            
            let hierarchy = [];
            let curr = target;
            for (let i = 0; i < 5; i++) {
                if (!curr) break;
                hierarchy.push({
                    tag: curr.tagName,
                    id: curr.id,
                    classes: curr.className,
                    onclick: !!curr.onclick
                });
                curr = curr.parentElement;
            }
            return hierarchy;
        })()
        """
        
        print(json.dumps(run_js(ws, diag_js), indent=2))
        ws.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
