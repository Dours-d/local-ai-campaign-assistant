
import requests
import json
import websocket

def get_dom():
    try:
        resp = requests.get("http://127.0.0.1:9222/json").json()
        target = next((t for t in resp if t['type'] == 'page'), None)
        if not target:
            print("No page found")
            return

        ws = websocket.create_connection(target['webSocketDebuggerUrl'])
        
        # Get DOM
        msg = {"id": 1, "method": "Runtime.evaluate", "params": {"expression": "document.body.outerHTML", "returnByValue": True}}
        ws.send(json.dumps(msg))
        result = json.loads(ws.recv())
        
        html = result['result']['result']['value']
        with open("data/current_dom_dump.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("DOM dumped to data/current_dom_dump.html")
        ws.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_dom()
