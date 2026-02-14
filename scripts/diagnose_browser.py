import json
import requests
import websocket
import sys

def get_browser_state():
    try:
        res = requests.get('http://localhost:9222/json')
        pages = res.json()
        if not pages:
            print("No pages found")
            return
        
        page_id = pages[0]['id']
        ws_url = pages[0]['webSocketDebuggerUrl']
        
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
