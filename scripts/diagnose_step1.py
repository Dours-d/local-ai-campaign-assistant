import requests
import json
import websocket
import time

CDP_URL = "http://127.0.0.1:9222/json"

def diagnose():
    try:
        r = requests.get(CDP_URL).json()
        target = next((t for t in r if t['type'] == 'page'), None)
        if not target:
            print("No page found.")
            return

        ws = websocket.create_connection(
            target['webSocketDebuggerUrl'].replace('localhost', '127.0.0.1'),
            suppress_origin_check=True,
            header={"Host": "127.0.0.1:9222"}
        )
        
        js = """
        JSON.stringify(Array.from(document.querySelectorAll('input, select, textarea')).map(i => ({
            tag: i.tagName,
            id: i.id,
            name: i.name,
            ph: i.placeholder,
            val: i.value,
            fc: i.getAttribute('formcontrolname'),
            cls: i.className,
            vis: i.offsetParent !== null
        })))
        """
        
        msg = {"id": 1, "method": "Runtime.evaluate", "params": {"expression": js, "returnByValue": True}}
        ws.send(json.dumps(msg))
        res = json.loads(ws.recv())
        
        if 'result' in res:
            items = json.loads(res['result']['result']['value'])
            print(json.dumps(items, indent=2))
        else:
            print(f"Error: {res}")
            
        ws.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    diagnose()
