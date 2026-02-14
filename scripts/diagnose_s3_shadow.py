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
            msg_id = 333
            ws.send(json.dumps({"id": msg_id, "method": "Runtime.evaluate", "params": {"expression": script, "returnByValue": True}}))
            while True:
                res = json.loads(ws.recv())
                if res.get('id') == msg_id: return res['result'].get('result', {}).get('value')

        print("--- Global Editor Search ---")
        js_find = """
        (function() {
            const results = [];
            // Check for shadow roots
            function findShadow(el) {
                if (el.shadowRoot) results.push({ tag: el.tagName, id: el.id, hasShadow: true });
                el.children && Array.from(el.children).forEach(findShadow);
            }
            findShadow(document.body);
            
            // Check for specific editors
            const editors = Array.from(document.querySelectorAll('*')).filter(el => 
                el.className && (typeof el.className === 'string') && (
                    el.className.includes('editor') || 
                    el.className.includes('ck-') || 
                    el.className.includes('ql-')
                )
            );
            return {
                shadows: results,
                editors: editors.slice(0, 10).map(e => ({ tag: e.tagName, class: e.className, id: e.id, text: e.innerText.substring(0, 50) }))
            };
        })()
        """
        results = run_js(js_find)
        print(f"Shadows and Editors: {json.dumps(results, indent=2)}")

        ws.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    diagnose()
