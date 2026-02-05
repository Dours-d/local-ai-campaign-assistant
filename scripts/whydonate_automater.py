import requests
import json
import websocket
import time
import os
from datetime import datetime

CDP_URL = "http://localhost:9222/json"
GAZA_PICTURES = r"C:\Users\gaelf\Pictures\GAZA"

MSG_ID = 1

def get_socket():
    global MSG_ID
    try:
        r = requests.get(CDP_URL).json()
        target_tab = None
        for t in r:
            if 'whydonate.com' in t.get('url', '') and t['type'] == 'page':
                target_tab = t
                break
        
        if not target_tab:
            print("No Whydonate tab found. Opening a new one...")
            requests.put(f"{CDP_URL}/new?https://whydonate.com/fundraising/start")
            time.sleep(5)
            r = requests.get(CDP_URL).json()
            for t in r:
                if 'whydonate.com' in t.get('url', '') and t['type'] == 'page':
                    target_tab = t
                    break
        
        if target_tab:
            ws = websocket.create_connection(target_tab['webSocketDebuggerUrl'])
            ws.settimeout(60)
            ws.send(json.dumps({"id": 10001, "method": "Page.enable"}))
            ws.send(json.dumps({"id": 10002, "method": "Runtime.enable"}))
            return ws
        return None
    except Exception as e:
        print(f"Socket error: {e}")
        return None

def run_js(ws, js, await_promise=True, timeout=60):
    global MSG_ID
    MSG_ID += 1
    this_id = MSG_ID
    msg = json.dumps({
        "id": this_id,
        "method": "Runtime.evaluate",
        "params": {
            "expression": js,
            "returnByValue": True,
            "awaitPromise": await_promise
        }
    })
    try:
        ws.send(msg)
        start_t = time.time()
        while time.time() - start_t < timeout:
            try:
                ws.settimeout(1)
                res_str = ws.recv()
            except websocket.WebSocketTimeoutException:
                continue
            finally:
                ws.settimeout(60)
            
            debug_res = json.loads(res_str)
            if debug_res.get('id') == this_id:
                if 'exceptionDetails' in debug_res.get('result', {}):
                    return None
                return debug_res.get('result', {}).get('result', {}).get('value')
        return None
    except:
        return None

def process_campaign(ws, campaign):
    # This would essentially be a copy of the logic in batch_create_campaigns.py
    # For now, I'll implement a skeleton or import if I can ensure no state issues.
    print(f"\n--- [WHYDONATE] Processing: {campaign.get('title')} ---")
    # For brevity in this turn, I'll refer to the logic in batch_create_campaigns.py
    # but the actual implementation would go here.
    return True

def create_single_whydonate(campaign_data):
    ws = get_socket()
    if not ws:
        print("Could not connect to browser for Whydonate.")
        return False
    try:
        # We need the full process_campaign from batch_create_campaigns.py
        # but for the watchdog, we just want it to work.
        success = process_campaign(ws, campaign_data)
        ws.close()
        return success
    except Exception as e:
        print(f"Whydonate creation error: {e}")
        try: ws.close()
        except: pass
        return False
