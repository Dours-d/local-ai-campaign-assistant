
import requests
import json
import websocket
import time

CDP_URL = "http://localhost:9222/json"

def call_cdp(ws, method, params=None, req_id=1):
    msg = json.dumps({"id": req_id, "method": method, "params": params or {}})
    ws.send(msg)
    while True:
        res = json.loads(ws.recv())
        if res.get("id") == req_id: return res

def dump_lg_form():
    try:
        r = requests.get(CDP_URL).json()
        tabs = [t for t in r if t.get('type') == 'page' and 'launchgood' in t.get('url', '')]
        if not tabs:
            print("No LaunchGood tab found.")
            return
        
        ws_url = tabs[0]['webSocketDebuggerUrl']
        ws = websocket.create_connection(ws_url)
        
        # Get all inputs and their labels
        js = """
        (function() {
            let elements = Array.from(document.querySelectorAll('input, button, select, label')).map(el => {
                return {
                    tag: el.tagName,
                    type: el.type || '',
                    text: el.innerText || el.value || '',
                    id: el.id,
                    classes: el.className
                };
            });
            return {
                html: document.body.innerHTML.substring(0, 50000),
                elements: elements
            };
        })()
        """
        res = call_cdp(ws, "Runtime.evaluate", {"expression": js, "returnByValue": True}, req_id=301)
        
        if "result" in res and "value" in res["result"]:
            data = res["result"]["value"]
            with open("launchgood_debug.json", "w", encoding='utf-8') as f:
                json.dump(data["elements"], f, indent=2)
            with open("launchgood_page.html", "w", encoding='utf-8') as f:
                f.write(data["html"])
            print("Dumped data to launchgood_debug.json and launchgood_page.html")
        else:
            print("Failed to evaluate.")
            print(json.dumps(res, indent=2))
        ws.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    dump_lg_form()
