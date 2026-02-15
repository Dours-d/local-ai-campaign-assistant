import requests
import json
import websocket

try:
    r = requests.get('http://localhost:9222/json').json()
    targets = [t for t in r if t.get('type') == 'page' and 'whydonate' in t.get('url', '')]
    if targets:
        target = targets[0]
        ws = websocket.create_connection(target['webSocketDebuggerUrl'])
        ws.send(json.dumps({'id': 1, 'method': 'Runtime.evaluate', 'params': {'expression': 'window.devicePixelRatio', 'returnByValue': True}}))
        res = json.loads(ws.recv())
        print(f"DevicePixelRatio: {res['result']['result'].get('value')}")
        
        # Reset zoom if it's not 1
        ws.send(json.dumps({'id': 2, 'method': 'Input.dispatchKeyEvent', 'params': {'type': 'rawKeyDown', 'windowsVirtualKeyCode': 48, 'modifiers': 2}})) # Ctrl+0
        ws.send(json.dumps({'id': 3, 'method': 'Input.dispatchKeyEvent', 'params': {'type': 'keyUp', 'windowsVirtualKeyCode': 48, 'modifiers': 2}}))
        print("Sent Ctrl+0 to reset zoom.")
        ws.close()
    else:
        print("No Whydonate tab found.")
except Exception as e:
    print(f"Error: {e}")
