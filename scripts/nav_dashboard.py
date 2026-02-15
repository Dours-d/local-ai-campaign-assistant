import requests, json, websocket
def navigate():
    try:
        r = requests.get("http://127.0.0.1:9222/json")
        tabs = r.json()
        target = [t for t in tabs if t.get('type') == 'page'][0]
        ws = websocket.create_connection(target['webSocketDebuggerUrl'])
        ws.send(json.dumps({'id': 1, 'method': 'Runtime.evaluate', 'params': {'expression': 'window.location.href = "https://whydonate.com/dashboard/fundraiser"'}}))
        ws.close()
        print("Navigation sent.")
    except Exception as e:
        print(f"Error: {e}")
if __name__ == "__main__":
    navigate()
