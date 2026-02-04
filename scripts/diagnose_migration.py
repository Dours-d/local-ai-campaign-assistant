
import requests
import json
import websocket

CDP_URL = "http://localhost:9222/json"

def run_js(ws, js):
    msg = json.dumps({
        "id": 12345,
        "method": "Runtime.evaluate",
        "params": {
            "expression": js,
            "returnByValue": True,
            "awaitPromise": True
        }
    })
    ws.send(msg)
    return ws.recv()

def diagnose():
    try:
        r = requests.get(CDP_URL).json()
        for t in r:
            if t.get('type') == 'page' and 'whydonate.com' in t.get('url', ''):
                print(f"--- Tab: {t.get('title')} ---")
                print(f"URL: {t.get('url')}")
                ws = websocket.create_connection(t['webSocketDebuggerUrl'])
                js = "document.body.innerText.substring(0, 1000)"
                res = run_js(ws, js)
                print(f"Content Snippet: {res[:1000]}\n")
                ws.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    diagnose()
