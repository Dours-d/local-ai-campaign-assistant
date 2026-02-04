
import json
import time
import requests
import websocket

CDP_URL = "http://localhost:9222/json"

_req_id = 0
def get_next_id():
    global _req_id
    _req_id += 1
    return _req_id

def call_cdp(ws, method, params=None):
    rid = get_next_id()
    msg = json.dumps({"id": rid, "method": method, "params": params or {}})
    ws.send(msg)
    while True:
        try:
            ws.settimeout(10.0) 
            raw = ws.recv()
            res = json.loads(raw)
            if res.get("id") == rid:
                return res
        except Exception as e:
            return None

def run_js(ws, js):
    return call_cdp(ws, "Runtime.evaluate", {"expression": js, "returnByValue": True, "awaitPromise": True})

def create_umbrella_fund():
    try:
        r = requests.get(CDP_URL).json()
        tabs = [t for t in r if t.get('type') == 'page' and 'launchgood' in t.get('url', '')]
        if not tabs:
            print("Action Required: Open LaunchGood in Chrome.")
            return
        
        ws = websocket.create_connection(tabs[0]['webSocketDebuggerUrl'])
        
        # Load Beneficiary Submissions
        submissions_path = "data/onboarding_submissions"
        beneficiary_updates = ""
        if os.path.exists(submissions_path):
            submission_files = [f for f in os.listdir(submissions_path) if f.endswith("_submission.json")]
            if submission_files:
                beneficiary_updates += "<h3>Active Beneficiary Submissions:</h3>"
                for sf in submission_files:
                    with open(os.path.join(submissions_path, sf), 'r', encoding='utf-8') as f:
                        sub = json.load(f)
                        beneficiary_updates += f"<h4>ID: {sub['beneficiary_id']} ({sub['display_name']})</h4>"
                        beneficiary_updates += f"<p><b>Title:</b> {sub['title']}</p>"
                        beneficiary_updates += f"<p><b>Story:</b> {sub['story']}</p>"
                        if sub.get('files'):
                            beneficiary_updates += "<p><b>Attached Media:</b></p><ul>"
                            for file_info in sub['files']:
                                # Handle both old list format and new dict format
                                p = file_info if isinstance(file_info, str) else file_info.get('path', '')
                                is_flagged = file_info.get('is_flagged', False) if isinstance(file_info, dict) else False
                                
                                bname = os.path.basename(p)
                                flag_str = " <b style='color:red;'>[FLAGGED: Graphic Content?]</b>" if is_flagged else ""
                                beneficiary_updates += f"<li>{bname}{flag_str}</li>"
                            beneficiary_updates += "</ul>"
                        beneficiary_updates += f"<p style='color: #2c3e50; background: #ecf0f1; padding: 10px; border-radius: 5px;'><b>Direct Support:</b> If you wish to support this family specifically, please include their ID <b>{sub['beneficiary_id']}</b> in your donation comment.</p><hr/>"

        # Fund Details
        title = "Global Gaza Resilience Fund: Unified Aid for 300+ Families"
        tagline = "A transparent, collective fund preserving the dignity and survival of 302 families in Gaza through zero-waste aid allocation."
        goal = 1500000 # ~€5000 * 300
        story = f"""
        <h2>Standing with the Families of Gaza</h2>
        <p>This is a <b>collective fund</b> designed to support over 300 families in Gaza. As an individual-managed project, we consolidate our efforts here to bypass the high bank fees and logistical barriers that prevent aid from reaching those in need.</p>
        
        {beneficiary_updates}

        <h3>How it Works:</h3>
        <ul>
            <li><b>Individual Allocation:</b> While this is one fund, every participating family has a unique <b>Beneficiary ID</b>.</li>
            <li><b>Zero-Waste:</b> By consolidating withdrawals, we avoid losing thousands of dollars to wire transfer fees.</li>
            <li><b>Total Transparency:</b> Weekly Monday audits track every cent from this fund to the individual families.</li>
        </ul>
        
        <p>We are the natural owners of our time and our solidarity. Join us in preserving life and dignity.</p>
        """
        
        # Step 1: Find Existing Draft or Create New
        run_js(ws, "window.location.hash = '/dashboard/campaigns'")
        time.sleep(5)
        
        # Check for existing campaign title
        js_find = f"""
        (function() {{
            let links = document.querySelectorAll('a');
            for (let link of links) {{
                if (link.innerText.includes("{title}")) {{
                    return link.href;
                }}
            }}
            return null;
        }})()
        """
        res_find = run_js(ws, js_find)
        campaign_url = res_find.get('result', {}).get('result', {}).get('value')
        
        if campaign_url:
            print(f"Found existing campaign at: {campaign_url}")
            # Navigate to Step 3 (Story) directly if possible, or start from beginning
            run_js(ws, f"window.location.href = '{campaign_url.replace('/detail/', '/edit/')}'")
            time.sleep(5)
        else:
            print("No existing draft found. Creating new...")
            run_js(ws, "window.location.hash = '/create/new/raising_for'")
            time.sleep(3)
            run_js(ws, "document.querySelectorAll('input[type=\"radio\"]')[0].click()") 
            time.sleep(1)
            run_js(ws, "document.querySelector('.lgx-button--default__cta-black').click()")
            time.sleep(4)
            # Basic Info (Step 2)
            js_step2 = f"""
            (function() {{
                let titleInput = document.querySelector('input[name="title"]') || document.querySelectorAll('input[type="text"]')[0];
                if (titleInput) {{
                    titleInput.value = `{title}`;
                    titleInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                }}
                let goalInput = document.querySelector('input[name="goal"]') || document.querySelectorAll('input[type="number"]')[0];
                if (goalInput) {{
                    goalInput.value = "{goal}";
                    goalInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                }}
                let taglineInput = document.querySelector('textarea[name="tagline"]') || document.querySelector('textarea');
                if (taglineInput) {{
                    taglineInput.value = `{tagline}`;
                    taglineInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                }}
            }})()
            """
            run_js(ws, js_step2)
            time.sleep(1)
            run_js(ws, "document.querySelector('.lgx-button--default__cta-black').click()")
            time.sleep(4)
        
        # Ensure we are on the Story tab
        run_js(ws, "window.location.hash = window.location.hash.split('?')[0].replace('basic_info', 'story')")
        time.sleep(3)

        # Step 3: Story
        js_step3 = f"""
        (function() {{
            let editor = document.querySelector('.ql-editor');
            if (editor) {{
                editor.innerHTML = `{story}`;
                editor.dispatchEvent(new Event('input', {{ bubbles: true }}));
            }}
        }})()
        """
        run_js(ws, js_step3)
        time.sleep(2)
        # Click Next/Save if visible
        run_js(ws, "document.querySelector('.lgx-button--default__cta-black')?.click()")
        time.sleep(2)
        
        print("Umbrella Fund successfully synced with latest beneficiary edits.")
        ws.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_umbrella_fund()
