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
            msg_id = 789
            ws.send(json.dumps({"id": msg_id, "method": "Runtime.evaluate", "params": {"expression": script, "returnByValue": True}}))
            while True:
                res = json.loads(ws.recv())
                if res.get('id') == msg_id: return res['result'].get('result', {}).get('value')

        print("--- APP-CREATE-FUNDRAISER Inner HTML ---")
        # Dump a simplified version of the inner HTML to avoid hitting size limits
        js_dump = """
        (function() {
            const el = document.querySelector('app-create-fundraiser');
            if (!el) return "NOT_FOUND";
            // Get all tags and their roles/classes in that component
            return Array.from(el.querySelectorAll('*')).map(e => ({
                tag: e.tagName,
                class: e.className,
                role: e.getAttribute('role'),
                contentEditable: e.contentEditable,
                placeholder: e.getAttribute('placeholder')
            })).filter(x => x.tag === 'TEXTAREA' || x.contentEditable === 'true' || x.tag === 'CKEDITOR' || x.class.includes('editor'));
        })()
        """
        results = run_js(js_dump)
        print(f"Interesting elements in form: {json.dumps(results, indent=2)}")

        ws.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    diagnose()
