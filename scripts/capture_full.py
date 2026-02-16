import requests, json, websocket, base64

def capture_full_page():
    try:
        r = requests.get("http://127.0.0.1:9222/json")
        tabs = r.json()
        target = [t for t in tabs if t.get('type') == 'page' and "whydonate.com" in t.get('url', '')][0]
        ws = websocket.create_connection(target['webSocketDebuggerUrl'], suppress_origin=True)
        
        # Get metrics
        msg = {"id": 1, "method": "Page.getLayoutMetrics"}
        ws.send(json.dumps(msg))
        res = json.loads(ws.recv())
        width = res['result']['contentSize']['width']
        height = res['result']['contentSize']['height']
        
        # Set viewport
        ws.send(json.dumps({"id": 2, "method": "Emulation.setDeviceMetricsOverride", "params": {
            "width": width, "height": height, "deviceScaleFactor": 1, "mobile": False
        }}))
        
        # Capture
        msg_id = 100
        ws.send(json.dumps({"id": msg_id, "method": "Page.captureScreenshot", "params": {"format": "png"}}))
        while True:
            res = json.loads(ws.recv())
            if res.get('id') == msg_id:
                if 'result' in res and 'data' in res['result']:
                    with open("data/step4_full.png", "wb") as f:
                        f.write(base64.b64decode(res['result']['data']))
                    print("Full screenshot saved to data/step4_full.png")
                else:
                    print(f"Error in response: {res}")
                break

        ws.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    capture_full_page()
