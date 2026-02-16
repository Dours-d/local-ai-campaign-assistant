import requests, json, websocket
def check_url():
    try:
        r = requests.get("http://127.0.0.1:9222/json")
        tabs = r.json()
        target = [t for t in tabs if t.get('type') == 'page' and "whydonate.com" in t.get('url', '')][0]
        ws = websocket.create_connection(target['webSocketDebuggerUrl'], suppress_origin=True)
        msg = {"id": 1, "method": "Runtime.evaluate", "params": {"expression": "window.location.href", "returnByValue": True}}
        ws.send(json.dumps(msg))
        res = json.loads(ws.recv())
        url = res.get('result', {}).get('result', {}).get('value')
        print(f"CURRENT_URL: {url}")
        ws.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_url()
