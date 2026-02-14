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
            msg_id = 111
            ws.send(json.dumps({"id": msg_id, "method": "Runtime.evaluate", "params": {"expression": script, "returnByValue": True}}))
            while True:
                res = json.loads(ws.recv())
                if res.get('id') == msg_id: return res['result'].get('result', {}).get('value')

        print("--- Finding Story Box by Label ---")
        js_find = """
        (function() {
            const labels = Array.from(document.querySelectorAll('div, p, span, label')).filter(el => el.innerText === 'Fundraiser Story');
            if (labels.length === 0) return "LABEL_NOT_FOUND";
            const label = labels[0];
            const parent = label.parentElement;
            const children = Array.from(parent.querySelectorAll('*'));
            return children.map(c => ({
                tag: c.tagName,
                class: c.className,
                html: c.outerHTML.substring(0, 100),
                contentEditable: c.contentEditable
            }));
        })()
        """
        results = run_js(js_find)
        print(f"Elements near 'Fundraiser Story' label: {json.dumps(results, indent=2)}")

        ws.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    diagnose()
