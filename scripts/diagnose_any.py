
import json
import time
import websocket
from PIL import Image
import io

def get_tab_url():
    import requests
    try:
        res = requests.get("http://127.0.0.1:9222/json")
        tabs = res.json()
        for tab in tabs:
            if "whydonate.com" in tab['url']:
                return tab
    except:
        return None
    return None

def diagnose():
    tab = get_tab_url()
    if not tab:
        print("No Whydonate tab found.")
        return
    
    ws_url = tab['webSocketDebuggerUrl']
    ws = websocket.create_connection(ws_url)
    
    def run_js(code):
        msg = json.dumps({"id": 1, "method": "Runtime.evaluate", "params": {"expression": code, "returnByValue": True}})
        ws.send(msg)
        res = json.loads(ws.recv())
        return res.get('result', {}).get('value')

    print(f"URL: {tab['url']}")
    
    html = run_js("document.body.innerHTML")
    if html:
        with open("data/diagnose_step_body.html", "w", encoding='utf-8') as f:
            f.write(html)
        print("HTML saved to data/diagnose_step_body.html")
    else:
        print("Failed to get HTML.")

    ws.close()

if __name__ == "__main__":
    diagnose()
