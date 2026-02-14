import requests
import websocket
import json

def main():
    try:
        r = requests.get("http://127.0.0.1:9222/json").json()
        target = next(t for t in r if t['type'] == 'page' and 'fundraising' in t.get('url', ''))
        ws = websocket.create_connection(target['webSocketDebuggerUrl'].replace('localhost', '127.0.0.1'), suppress_origin_check=True)
        
        script = """
        (function() {
            return {
                url: window.location.href,
                body: document.body.innerText.substring(0, 1000),
                inputs: Array.from(document.querySelectorAll('input')).map(i => ({
                    placeholder: i.placeholder,
                    id: i.id,
                    className: i.className,
                    type: i.type,
                    value: i.value,
                    formControl: i.getAttribute('formcontrolname')
                })),
                stepper: !!document.querySelector('mat-stepper, .mat-stepper-horizontal, .mat-stepper-vertical'),
                frames: Array.from(document.querySelectorAll('iframe')).map(f => f.src)
            };
        })()
        """
        msg = {"id": 1, "method": "Runtime.evaluate", "params": {"expression": script, "returnByValue": True}}
        ws.send(json.dumps(msg))
        res = json.loads(ws.recv())
        data = res['result']['result'].get('value', 'NOT_FOUND')
        
        with open("data/debug_info.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print("Debug info captured to data/debug_info.json")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
