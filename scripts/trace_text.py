import requests
import json
import websocket
import time

CDP_URL = "http://localhost:9222/json"

def run_js(ws, js):
    msg = {"id": 1, "method": "Runtime.evaluate", "params": {"expression": js, "returnByValue": True}}
    ws.send(json.dumps(msg))
    res = json.loads(ws.recv())
    return res.get('result', {}).get('result', {}).get('value')

def main():
    try:
        r = requests.get(CDP_URL).json()
        target = next((t for t in r if 'whydonate.com' in t.get('url', '') and t.get('type') == 'page'), None)
        if not target:
            print("No Whydonate page found")
            return
        
        ws = websocket.create_connection(target['webSocketDebuggerUrl'], suppress_origin=True)
        
        diag_js = """
        (function() {
            const allText = document.body.innerText.substring(0, 1000);
            const headers = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, .step-title, mat-step-header'))
                .map(h => h.innerText.trim());
            const currentStep = document.querySelector('mat-step-header[aria-selected="true"]')?.innerText || "Not Found";
            
            return {
                current_step_header: currentStep,
                all_headers: headers,
                first_1000_chars: allText
            };
        })()
        """
        
        print(json.dumps(run_js(ws, diag_js), indent=2))
        ws.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
