import json
import requests
import websocket
import sys

def get_browser_state():
    try:
        r = requests.get('http://localhost:9222/json')
        tabs = r.json()
        # Find the correct tab: must be a page and contain whydonate
        pages = [t for t in tabs if t.get('type') == 'page' and 'whydonate.com' in t.get('url', '')]
        if not pages:
            # Fallback to any page if no whydonate page found
            pages = [t for t in tabs if t.get('type') == 'page']
            
        if not pages:
            print("No browser pages found")
            return
        
        target = pages[0]
        page_id = target['id']
        ws_url = target['webSocketDebuggerUrl']
        print(f"Connecting to: {target.get('url')} (Title: {target.get('title')})")
        
        ws = websocket.create_connection(ws_url)
        
        def run_js(script):
            msg = {'id': 1, 'method': 'Runtime.evaluate', 'params': {'expression': script, 'returnByValue': True}}
            ws.send(json.dumps(msg))
            resp = json.loads(ws.recv())
            return resp.get('result', {}).get('result', {}).get('value')

        url = run_js("window.location.href")
        has_login = run_js("document.body.innerText.includes('Login')")
        user_name = run_js("document.querySelector('.user-name')?.innerText || 'NOT_FOUND'")
        
        print(f"URL: {url}")
        print(f"Has 'Login' text: {has_login}")
        print(f"User Name element: {user_name}")
        
        ws.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    get_browser_state()
