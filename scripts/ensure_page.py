import requests, json, websocket, base64, time

def ensure_page_and_screenshot():
    try:
        r = requests.get("http://127.0.0.1:9222/json")
        tabs = r.json()
        
        # Look for a page
        page_tabs = [t for t in tabs if t.get('type') == 'page']
        
        if not page_tabs:
            print("No page found. Creating new page...")
            requests.put("http://127.0.0.1:9222/json/new?https://whydonate.com/en/start-fundraiser/")
            time.sleep(5)
            tabs = requests.get("http://127.0.0.1:9222/json").json()
            page_tabs = [t for t in tabs if t.get('type') == 'page']
        
        if not page_tabs:
            print("Failed to find or create page.")
            return

        target = page_tabs[0]
        ws = websocket.create_connection(target['webSocketDebuggerUrl'])
        
        # Take screenshot
        ws.send(json.dumps({'id': 1, 'method': 'Page.captureScreenshot'}))
        
        start_time = time.time()
        while time.time() - start_time < 15:
            res = json.loads(ws.recv())
            if res.get('id') == 1:
                if 'result' in res:
                    data = res['result']['data']
                    with open("data/current_state.png", "wb") as f:
                        f.write(base64.b64decode(data))
                    print(f"Screenshot saved. URL: {target.get('url')}")
                else:
                    print(f"Error in CDP response: {res}")
                break
        ws.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    ensure_page_and_screenshot()
