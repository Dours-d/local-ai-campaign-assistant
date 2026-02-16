import requests
import json
import websocket

CDP_URL = "http://localhost:9222/json"

def main():
    try:
        r = requests.get(CDP_URL).json()
        target = next((t for t in r if 'whydonate.com' in t.get('url', '') and t.get('type') == 'page'), None)
        if not target:
            print("No Whydonate page found")
            return
        
        ws = websocket.create_connection(target['webSocketDebuggerUrl'], suppress_origin=True)
        
        js = """
        (function() {
            const ub = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, span, div')).find(el => el.innerText.includes("Unsupported Browser"));
            return ub ? {innerText: ub.innerText, visible: ub.offsetWidth > 0, classes: ub.className} : "Not Found";
        })()
        """
        msg = {"id": 1, "method": "Runtime.evaluate", "params": {"expression": js, "returnByValue": True}}
        ws.send(json.dumps(msg))
        res = json.loads(ws.recv())
        print(json.dumps(res.get('result', {}).get('result', {}).get('value'), indent=2))
        ws.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
