
import requests
import websocket
import json
import time

CDP_URL = "http://localhost:9222/json"

def run_js(ws, js, this_id=1):
    msg = {
        "id": this_id,
        "method": "Runtime.evaluate",
        "params": {"expression": js, "returnByValue": True}
    }
    ws.send(json.dumps(msg))
    start_t = time.time()
    while time.time() - start_t < 10:
        try:
            ws.settimeout(1)
            res = json.loads(ws.recv())
            if res.get('id') == this_id:
                # The response is nested: res['result']['result']['value']
                return res.get('result', {}).get('result', {}).get('value')
        except websocket.WebSocketTimeoutException:
            continue
    return None

def main():
    r = requests.get(CDP_URL).json()
    tabs = [t for t in r if 'whydonate.com' in t.get('url', '') and t['type'] == 'page']
    target = next((t for t in tabs if 'dashboard' in t.get('url', '').lower()), None)
    if not target:
        print("No dashboard tab found.")
        return

    ws = websocket.create_connection(target['webSocketDebuggerUrl'])
    print(f"Connected to: {target['url']}")
    
    # Basic test
    test_res = run_js(ws, "1+1")
    print(f"Basic connectivity test (1+1): {test_res}")
    
    # Check login status
    page_text = run_js(ws, "document.body.innerText")
    if page_text is None:
        print("Failed to get innerText. Page might not be ready or evaluation failed.")
        return
    
    is_logged_in = "Log in" not in page_text and "Sign up" not in page_text
    print(f"Logged in: {is_logged_in}")

    # List all links
    links = run_js(ws, "Array.from(document.querySelectorAll('a')).map(el => ({text: el.innerText.trim(), href: el.href}))")
    if links:
        print(f"Total Links found: {len(links)}")
        for link in links:
             print(f"  - {link['text']} -> {link['href']}")
    else:
        print("No links found.")

    ws.close()

if __name__ == "__main__":
    main()
