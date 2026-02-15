import requests, json, websocket

def test_get_step():
    r = requests.get("http://127.0.0.1:9222/json")
    tabs = r.json()
    target = [t for t in tabs if t.get('type') == 'page' and "whydonate.com" in t.get('url', '')][0]
    ws = websocket.create_connection(target['webSocketDebuggerUrl'])
    
    def run_js(js):
        msg = {"id": 1, "method": "Runtime.evaluate", "params": {"expression": js, "returnByValue": True}}
        ws.send(json.dumps(msg))
        res = json.loads(ws.recv())
        return res.get('result', {}).get('result', {}).get('value')

    body = run_js("document.body.innerText")
    print(f"Body length: {len(body) if body else 0}")
    
    # Simulate get_step logic
    def get_step_sim(body):
        if any(x in body for x in ["Launch Fundraiser", "Launch and share", "Target amount", "Target Amount"]): return 4
        if any(x in body for x in ["Fundraiser Title", "Fundraiser Story", "Your story", "Unique link"]): return 3
        if any(x in body for x in ["Who is this fundraiser for?", "collecting money for?", "Someone Else"]): return 2
        if any(x in body for x in ["What is your address", "which language do you prefer", "Let's Get Your Fundraiser Started"]): return 1
        
        if any(x in body for x in ["Create New Account", "Login to your account", "Already have an account?"]) and \
           not any(x in body for x in ["Step 1/4", "Step 2/4", "Step 3/4", "Step 4/4"]):
            return 0
        return 1

    step = get_step_sim(body)
    print(f"Detected Step: {step}")
    ws.close()

if __name__ == "__main__":
    test_get_step()
