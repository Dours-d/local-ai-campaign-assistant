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
            msg_id = 777
            ws.send(json.dumps({"id": msg_id, "method": "Runtime.evaluate", "params": {"expression": script, "returnByValue": True}}))
            while True:
                res = json.loads(ws.recv())
                if res.get('id') == msg_id: return res['result'].get('result', {}).get('value')

        print("--- Scrolling and Finding Goal ---")
        run_js("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(1)
        
        js_find = """
        (function() {
            const all = Array.from(document.querySelectorAll('input, [formcontrolname], label, span'));
            const goalMatches = all.filter(el => 
                (el.innerText || "").includes("Goal") || 
                (el.getAttribute('formcontrolname') || "").includes("goal") ||
                (el.getAttribute('placeholder') || "").includes("Goal")
            );
            return goalMatches.map(m => ({
                tag: m.tagName,
                id: m.id,
                class: m.className,
                name: m.getAttribute('formcontrolname'),
                placeholder: m.getAttribute('placeholder'),
                text: m.innerText.substring(0, 50)
            }));
        })()
        """
        results = run_js(js_find)
        print(f"Goal field candidates: {json.dumps(results, indent=2)}")

        ws.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    diagnose()
