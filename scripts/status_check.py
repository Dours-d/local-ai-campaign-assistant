import requests
import json
import websocket
import time

CDP_URL = "http://127.0.0.1:9222/json"

def diagnose():
    try:
        r = requests.get(CDP_URL).json()
        target = next((t for t in r if t['type'] == 'page' and 'whydonate.com' in t.get('url', '')), None)
        if not target:
            print("WhyDonate page not found.")
            return
            
        ws = websocket.create_connection(target['webSocketDebuggerUrl'].replace('localhost', '127.0.0.1'))
        
        def run_js(script):
            msg_id = 999
            ws.send(json.dumps({"id": msg_id, "method": "Runtime.evaluate", "params": {"expression": script, "returnByValue": True}}))
            while True:
                res = json.loads(ws.recv())
                if res.get('id') == msg_id: return res['result'].get('result', {}).get('value')

        print(f"URL: {run_js('window.location.href')}")
        print(f"Title: {run_js('document.title')}")
        print(f"Step text: {run_js('document.body.innerText.match(/Step (\\\\d)\\\\/4/)?.[0]')}")
        print(f"H1: {run_js('document.querySelector(\"h1\")?.innerText')}")

        ws.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    diagnose()
