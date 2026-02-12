
import json
import requests
import websocket
import random

PORT = "9222"

def get_whatsapp_tab():
    try:
        response = requests.get(f"http://127.0.0.1:{PORT}/json")
        tabs = response.json()
        for tab in tabs:
            if "whatsapp" in tab.get("url", "") and tab.get("type") == "page":
                return tab
    except Exception as e:
        print(f"Error connecting to browser: {e}")
    return None

def send_cdp_command(ws, method, params):
    cmd_id = random.randint(1, 1000000)
    msg = json.dumps({"id": cmd_id, "method": method, "params": params})
    ws.send(msg)
    while True:
        res = json.loads(ws.recv())
        if res.get("id") == cmd_id:
            return res.get("result", {})

def probe_labels():
    tab = get_whatsapp_tab()
    if not tab:
        print("WhatsApp tab not found.")
        return

    ws_url = tab["webSocketDebuggerUrl"]
    ws = websocket.create_connection(ws_url)
    
    # JavaScript to find Label related elements
    js = """
    (function() {
        const results = {};
        
        // 1. Find the Labels button in the menu
        const labelButtons = Array.from(document.querySelectorAll('div[role="button"], span[title]'))
            .filter(el => /label/i.test(el.innerText) || /label/i.test(el.title));
        
        results.labelButtons = labelButtons.map(el => ({
            text: el.innerText,
            title: el.title,
            html: el.outerHTML.substring(0, 500)
        }));

        // 2. Try to find the word 'creations' regardless of where it is
        const creationsFound = Array.from(document.querySelectorAll('*'))
            .filter(el => el.children.length === 0 && /creations/i.test(el.innerText));
            
        results.creationsContext = creationsFound.map(el => ({
             tag: el.tagName,
             text: el.innerText,
             parent: el.parentElement.tagName
        }));

        // 3. Look for elements with 'data-icon="label"'
        const labelIcons = Array.from(document.querySelectorAll('[data-icon*="label"]'));
        results.labelIcons = labelIcons.map(el => el.outerHTML);

        return results;
    })()
    """
    
    result = send_cdp_command(ws, "Runtime.evaluate", {"expression": js, "returnByValue": True})
    print(json.dumps(result.get("result", {}).get("value", {}), indent=2))
    ws.close()

if __name__ == "__main__":
    probe_labels()
