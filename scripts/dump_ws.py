import requests
import json
import websocket
import time

CDP_URL = "http://127.0.0.1:9222/json"

def main():
    try:
        r = requests.get(CDP_URL).json()
        target = None
        for t in r:
             if 'whydonate.com' in t.get('url', '') and t['type'] == 'page':
                 target = t
                 break
        if not target:
            print("No target tab.")
            return
            
        ws = websocket.create_connection(target['webSocketDebuggerUrl'])
        ws.settimeout(1)
        print(f"Listening to: {target['url']}")
        
        start_t = time.time()
        while time.time() - start_t < 10:
            try:
                msg = ws.recv()
                print(f"MSG: {msg[:200]}...")
            except websocket.WebSocketTimeoutException:
                print("Wait...")
        ws.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
