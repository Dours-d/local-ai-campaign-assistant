import requests
import json
import websocket
import time
import os
from dotenv import load_dotenv

load_dotenv()

CDP_URL = "http://127.0.0.1:9222/json"
EMAIL = os.getenv("ADMIN_EMAIL")
PASSWORD = os.getenv("ADMIN_PASSWORD")

def perform_login():
    try:
        r = requests.get(CDP_URL).json()
        target = next((t for t in r if t.get('type') == 'page' and 'whydonate' in t.get('url', '')), r[0])
        ws = websocket.create_connection(target['webSocketDebuggerUrl'])
        
        def run_js(js):
            msg = {"id": 1, "method": "Runtime.evaluate", "params": {"expression": js, "returnByValue": True}}
            ws.send(json.dumps(msg))
            res = json.loads(ws.recv())
            return res.get('result', {}).get('result', {}).get('value')

        url = run_js('window.location.href')
        print(f"Current URL: {url}")
        
        if "wp-login.php" in url:
            print("Detected WordPress login page.")
            username_to_try = EMAIL
            print(f"Trying username/email: {username_to_try}")
            js_fill = f"""
            (function() {{
                const user = document.getElementById('user_login');
                const pass = document.getElementById('user_pass');
                const submit = document.getElementById('wp-submit');
                if (user && pass) {{
                    user.value = {json.dumps(username_to_try)};
                    pass.value = {json.dumps(PASSWORD)};
                    submit.click();
                    return "SUBMITTED";
                }}
                return "FIELDS_NOT_FOUND";
            }})()
            """
            status = run_js(js_fill)
            print(f"WP Login Status: {status}")
            time.sleep(10)
        elif "account/login" in url:
            print("Detected standard account login page.")
            # Standard app login might have ID-based selectors
            js_fill = f"""
            (function() {{
                const email = document.getElementById('loginEmail') || document.querySelector('input[type="email"]');
                const pass = document.getElementById('loginPassword') || document.querySelector('input[type="password"]');
                const btn = document.getElementById('userLogin') || Array.from(document.querySelectorAll('button')).find(b => b.innerText.trim() === 'Login');
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
            print(f"App Login Status: {status}")
            time.sleep(10)
        else:
            print("Not on a recognized login page. Navigating to /en/login...")
            run_js('window.location.href = "https://whydonate.com/en/login"')
            time.sleep(8)
            # Recursively try again or just end and user can run it again
            print("Navigated. Please check state and re-run.")

        print(f"URL after: {run_js('window.location.href')}")
        ws.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    perform_login()
