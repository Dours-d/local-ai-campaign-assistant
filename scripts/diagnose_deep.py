import requests
import json
import websocket
import time

CDP_URL = "http://127.0.0.1:9222/json"

def diagnose():
    try:
        r = requests.get(CDP_URL).json()
        target = next((t for t in r if t['type'] == 'page' and 'whydonate.com' in t.get('url', '')), None)
        if not target: return
        ws = websocket.create_connection(target['webSocketDebuggerUrl'].replace('localhost', '127.0.0.1'))
        
        def run_js(script):
            msg_id = 1616
            ws.send(json.dumps({"id": msg_id, "method": "Runtime.evaluate", "params": {"expression": script, "returnByValue": True}}))
            while True:
                res = json.loads(ws.recv())
                if res.get('id') == msg_id: return res['result'].get('result', {}).get('value')

        print("--- Deep Requirement Audit ---")
        js_audit = """
        (function() {
            const all = Array.from(document.querySelectorAll('*'));
            const requirements = all.filter(el => {
                const text = (el.innerText || "").toLowerCase();
                return text.includes("required") || text.includes("missing") || text.includes("invalid") || text.includes("error");
            }).map(el => ({
                tag: el.tagName,
                text: el.innerText.substring(0, 50),
                visible: el.offsetParent !== null,
                class: el.className
            }));
            
            const nextBtn = document.getElementById('saveBtn');
            const nextBtnState = nextBtn ? {
                disabled: nextBtn.disabled,
                html: nextBtn.outerHTML
            } : "NOT_FOUND";

            return {
                requirements,
                nextBtnState
            };
        })()
        """
        results = run_js(js_audit)
        print(json.dumps(results, indent=2))

        ws.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    diagnose()
