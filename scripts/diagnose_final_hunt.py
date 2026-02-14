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
            msg_id = 9999
            ws.send(json.dumps({"id": msg_id, "method": "Runtime.evaluate", "params": {"expression": script, "returnByValue": True}}))
            while True:
                res = json.loads(ws.recv())
                if res.get('id') == msg_id: return res['result'].get('result', {}).get('value')

        print("--- Global Iframe Search ---")
        js_find = """
        (function() {
            const iframes = Array.from(document.querySelectorAll('iframe'));
            return iframes.map(f => ({
                id: f.id,
                src: f.src,
                class: f.className
            }));
        })()
        """
        results = run_js(js_find)
        print(f"Iframes found: {json.dumps(results, indent=2)}")
        
        print("--- Global Text Hunt ---")
        js_text = """
        (function() {
            const text = document.body.innerText;
            const segments = text.split('\\n').filter(s => 
                s.toLowerCase().includes('goal') || s.toLowerCase().includes('target') || s.includes('€') || s.includes('$')
            );
            return segments;
        })()
        """
        text_results = run_js(js_text)
        print(f"Text segments found: {json.dumps(text_results, indent=2)}")

        ws.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    diagnose()
