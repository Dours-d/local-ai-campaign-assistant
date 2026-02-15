import requests, json, websocket, base64, time, os

def take_state_screenshot():
    try:
        r = requests.get("http://127.0.0.1:9222/json")
        tabs = r.json()
        # Find the first page tab
        page_tabs = [t for t in tabs if t.get('type') == 'page']
        if not page_tabs:
            print("No page tab found.")
            return
            
        target = page_tabs[0]
        print(f"Targeting: {target.get('title')} ({target.get('url')})")
        ws = websocket.create_connection(target['webSocketDebuggerUrl'])
        
        ws.send(json.dumps({'id': 1, 'method': 'Page.captureScreenshot'}))
        
        start_time = time.time()
        while time.time() - start_time < 15:
            res = json.loads(ws.recv())
            if res.get('id') == 1:
                if 'result' in res:
                    data = res['result']['data']
                    with open("data/current_state.png", "wb") as f:
                        f.write(base64.b64decode(data))
                    print("Screenshot saved to data/current_state.png")
                else:
                    print(f"Error: {res}")
                break
        ws.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    take_state_screenshot()
