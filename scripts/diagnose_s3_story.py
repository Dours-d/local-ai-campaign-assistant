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
            msg_id = 456
            ws.send(json.dumps({"id": msg_id, "method": "Runtime.evaluate", "params": {"expression": script, "returnByValue": True}}))
            while True:
                res = json.loads(ws.recv())
                if res.get('id') == msg_id: return res['result'].get('result', {}).get('value')

        print("--- Step 3 Story Search ---")
        js_search = """
        (function() {
            const all = Array.from(document.querySelectorAll('*'));
            const matches = all.filter(el => 
                (el.innerText || "").includes("Tell your story with heart") ||
                (el.getAttribute('placeholder') || "").includes("Tell your story")
            );
            return matches.slice(0, 10).map(m => ({
                tag: m.tagName,
                className: m.className,
                placeholder: m.getAttribute('placeholder'),
                text: m.innerText.substring(0, 50),
                contentEditable: m.contentEditable,
                id: m.id
            }));
        })()
        """
        results = run_js(js_search)
        print(f"Matches for 'Story' placeholder: {json.dumps(results, indent=2)}")

        print("--- Frame Search ---")
        frames = run_js("Array.from(document.querySelectorAll('iframe')).map(f => ({ src: f.src, id: f.id, className: f.className }))")
        print(f"Iframes: {json.dumps(frames, indent=2)}")

        ws.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    diagnose()
