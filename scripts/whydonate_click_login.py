import requests
import websocket
import json
import time

def submit_login():
    try:
        r = requests.get("http://127.0.0.1:9222/json").json()
        target = next((t for t in r if t['type'] == 'page'), None)
        if not target:
            print("No page target found")
            return False
        
        ws_url = target['webSocketDebuggerUrl'].replace('localhost', '127.0.0.1')
        ws = websocket.create_connection(ws_url, suppress_origin_check=True)
        
        # JS to find and click Login button on the form
        js = """
        (function() {
            // Target the button with text "Login" that is likely the submit button
            const buttons = Array.from(document.querySelectorAll("button"));
            const loginBtn = buttons.find(b => b.innerText.trim() === "Login" && b.offsetParent !== null);
            if (loginBtn) {
                loginBtn.click();
                return "SUCCESS";
            }
            return "NOT_FOUND";
        })()
        """
        
        msg = {
            "id": 1,
            "method": "Runtime.evaluate",
            "params": {
                "expression": js,
                "returnByValue": True
            }
        }
        ws.send(json.dumps(msg))
        res = json.loads(ws.recv())
        status = res['result']['result']['value']
        print(f"Click status: {status}")
        
        ws.close()
        return status == "SUCCESS"
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    submit_login()
