import requests
import json
import websocket
import time

CDP_URL = "http://localhost:9222/json"

def run_js(ws, js):
    msg = {"id": 1, "method": "Runtime.evaluate", "params": {"expression": js, "returnByValue": True}}
    ws.send(json.dumps(msg))
    while True:
        res = json.loads(ws.recv())
        if res.get('id') == 1:
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
            const els = Array.from(document.querySelectorAll('*'));
            const targets = els.filter(el => el.innerText && (el.innerText.trim() === 'Yourself' || el.innerText.trim() === 'Someone Else'));
            return targets.map(el => {
                const card = el.closest('mat-card, .mat-mdc-card, div[role="button"], .category-card');
                return {
                    text: el.innerText.trim(),
                    tag: el.tagName,
                    classes: el.className,
                    card_tag: card ? card.tagName : null,
                    card_classes: card ? card.className : null,
                    card_aria_checked: card ? card.getAttribute('aria-checked') : null,
                    card_selected: card ? card.classList.contains('selected') || card.classList.contains('active') : null
                };
            });
        })()
        """
        
        print(json.dumps(run_js(ws, diag_js), indent=2))
        ws.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
