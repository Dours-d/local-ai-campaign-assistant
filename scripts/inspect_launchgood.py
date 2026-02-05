import websocket
import json
import time
import requests

CDP_URL = "http://localhost:9222/json"

def get_socket():
    try:
        r = requests.get(CDP_URL).json()
        target_tab = None
        for t in r:
            # Look for LaunchGood tab
            if 'launchgood.com' in t.get('url', '') and t['type'] == 'page':
                target_tab = t
                break
        
        if target_tab:
            print(f"Connecting to {target_tab['webSocketDebuggerUrl']}...", flush=True)
            ws = websocket.create_connection(target_tab['webSocketDebuggerUrl'], suppress_origin=True)
            ws.settimeout(20)
            ws.send(json.dumps({"id": 1, "method": "Page.enable"}))
            ws.send(json.dumps({"id": 2, "method": "Runtime.enable"}))
            return ws
        return None
    except Exception as e:
        print(f"Socket error: {e}", flush=True)
        return None

def main():
    ws = get_socket()
    if not ws:
        print("No socket found for LaunchGood tab. Please open https://www.launchgood.com/new-campaign", flush=True)
        return

    print("Connected. Capturing DOM...", flush=True)
    js_dump = "document.documentElement.outerHTML"
    
    msg_id = 999
    msg = json.dumps({
        "id": msg_id,
        "method": "Runtime.evaluate",
        "params": {
            "expression": js_dump,
            "returnByValue": True
        }
    })
    ws.send(msg)
    
    start_time = time.time()
    while time.time() - start_time < 10:
        try:
            ws.settimeout(2)
            res = ws.recv()
            data = json.loads(res)
            if data.get('id') == msg_id:
                html = data.get('result', {}).get('result', {}).get('value', '')
                with open("data/launchgood_dom.html", "w", encoding="utf-8") as f:
                    f.write(html)
                print("Saved to data/launchgood_dom.html", flush=True)
                return
        except Exception as e:
            pass
            
    print("Failed to capture.")
    ws.close()

if __name__ == "__main__":
    main()
