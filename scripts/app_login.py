import requests, json, websocket, time, os
from dotenv import load_dotenv

load_dotenv()
EMAIL = os.getenv("ADMIN_EMAIL")
PASSWORD = os.getenv("ADMIN_PASSWORD")

def perform_app_login():
    try:
        r = requests.get("http://127.0.0.1:9222/json")
        tabs = r.json()
        target = [t for t in tabs if t.get('type') == 'page'][0]
        ws = websocket.create_connection(target['webSocketDebuggerUrl'])
        
        def run_js(js):
            msg = {"id": 1, "method": "Runtime.evaluate", "params": {"expression": js, "returnByValue": True}}
            ws.send(json.dumps(msg))
            res = json.loads(ws.recv())
            return res.get('result', {}).get('result', {}).get('value')

        print("Navigating to https://whydonate.com/en/login...")
        run_js('window.location.href = "https://whydonate.com/en/login"')
        time.sleep(8)
        
        js_fill = f"""
        (function() {{
            const email = document.getElementById('loginEmail') || document.querySelector('input[type="email"]');
            const pass = document.getElementById('loginPassword') || document.querySelector('input[type="password"]');
            const btn = document.getElementById('userLogin') || Array.from(document.querySelectorAll('button')).find(b => b.innerText.trim().includes('Login'));
            if (email && pass && btn) {{
                email.value = {json.dumps(EMAIL)};
                email.dispatchEvent(new Event('input', {{bubbles:true}}));
                pass.value = {json.dumps(PASSWORD)};
                pass.dispatchEvent(new Event('input', {{bubbles:true}}));
                btn.click();
                return "SUBMITTED";
            }}
            return "FIELDS_NOT_FOUND";
        }})()
        """
        status = run_js(js_fill)
        print(f"Login Status: {status}")
        time.sleep(10)
        print(f"Final URL: {run_js('window.location.href')}")
        ws.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    perform_app_login()
