import requests
import json
import websocket
import time

CDP_URL = "http://127.0.0.1:9222/json"

def find_options():
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
        
        def send(method, params=None):
            mid = int(time.time() * 1000) % 1000000
            msg = {"id": mid, "method": method}
            if params: msg["params"] = params
            ws.send(json.dumps(msg))
            return mid

        def recv(mid):
            start = time.time()
            while time.time() - start < 10:
                res = json.loads(ws.recv())
                if res.get('id') == mid: return res
            return None

        # Focus
        js_focus = """
        (function() {
            const addr = document.querySelector('input[formcontrolname="location"]');
            if (addr) {
                addr.focus();
                addr.scrollIntoView();
                return true;
            }
            return false;
        })()
        """
        send("Runtime.evaluate", {"expression": js_focus})
        time.sleep(1)
        
        # Type
        for char in "Amman":
            send("Input.dispatchKeyEvent", {"type": "char", "text": char})
            time.sleep(0.05)
        
        print("Typed Amman. Waiting for dropdown...")
        time.sleep(4)
        
        # Scan DOM
        js_scan = """
        JSON.stringify(Array.from(document.querySelectorAll('*')).filter(el => 
            el.innerText && el.innerText.includes('Amman') && el.offsetParent !== null && el.tagName !== 'SCRIPT' && el.tagName !== 'STYLE'
        ).map(el => ({
            tag: el.tagName,
            cls: el.className,
            text: el.innerText.substring(0, 100).replace(/\\n/g, ' '),
            id: el.id
        })))
        """
        mid = send("Runtime.evaluate", {"expression": js_scan, "returnByValue": True})
        res = recv(mid)
        
        if res and 'result' in res:
            items = json.loads(res['result']['result']['value'])
            print("--- Visible elements containing 'Amman' ---")
            print(json.dumps(items, indent=2))
        else:
            print("Search failed or no elements found.")
            
        ws.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_options()
