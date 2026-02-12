import requests
import json
import websocket
import time
import os

CDP_URL = "http://127.0.0.1:9222/json"

class WhyDonateScraper:
    def __init__(self, cdp_url=CDP_URL):
        self.cdp_url = cdp_url
        self.ws = None

    def connect(self):
        try:
            r = requests.get(self.cdp_url).json()
            target = next((t for t in r if t['type'] == 'page'), None)
            if not target: return False
            self.ws = websocket.create_connection(
                target['webSocketDebuggerUrl'].replace('localhost', '127.0.0.1'),
                suppress_origin_check=True,
                header={"Host": "127.0.0.1:9222"}
            )
            return True
        except: return False

    def send_cdp(self, method, params=None):
        msg_id = int(time.time() * 1000) % 1000000
        msg = {"id": msg_id, "method": method}
        if params: msg["params"] = params
        self.ws.send(json.dumps(msg))
        return msg_id

    def recv_until_id(self, msg_id, timeout=10):
        start = time.time()
        while time.time() - start < timeout:
            try:
                self.ws.settimeout(0.5)
                res = json.loads(self.ws.recv())
                if res.get('id') == msg_id: return res
            except: continue
        return None

    def run_js(self, js):
        mid = self.send_cdp("Runtime.evaluate", {"expression": js, "returnByValue": True})
        res = self.recv_until_id(mid)
        if res and 'result' in res:
            return res['result'].get('result', {}).get('value')
        return None

    def take_screenshot(self, filename):
        mid = self.send_cdp("Page.captureScreenshot")
        res = self.recv_until_id(mid, timeout=15)
        if res and 'result' in res:
            import base64
            with open(filename, "wb") as f:
                f.write(base64.b64decode(res['result']['data']))
            print(f"Screenshot saved to {filename}")
            return True
        return False

    def scrape(self):
        print("Navigating to Fundraisers Dashboard...")
        self.run_js("window.location.href = 'https://whydonate.com/fundraisers/'")
        time.sleep(5)
        print(f"Current URL: {self.run_js('window.location.href')}")
        print("Scrolling and Scraping...")
        
        # Scroll to bottom to load all fundraisers
        self.run_js("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(5)
        self.run_js("window.scrollTo(0, 0)")
        time.sleep(2)
        self.take_screenshot("data/dashboard_full_view.png")
        
        js_scrape = """
        (function() {
            const cards = Array.from(document.querySelectorAll('mat-card'));
            return cards.map(c => {
                const title = c.querySelector('mat-card-title')?.innerText || "";
                const link_elm = c.querySelector('a[href*="/fundraising/"]');
                let link = link_elm ? link_elm.href : "";
                
                // Fallback: search for any link in the card
                if (!link) {
                    const all_links = Array.from(c.querySelectorAll('a'));
                    const wd_link = all_links.find(a => a.href.includes('/fundraising/') && !a.href.includes('/start'));
                    if (wd_link) link = wd_link.href;
                }
                
                return {title, link};
            });
        })()
        """
        data = self.run_js(js_scrape)
        return data

if __name__ == "__main__":
    scraper = WhyDonateScraper()
    if scraper.connect():
        results = scraper.scrape()
        print(json.dumps(results, indent=2))
        with open("data/dashboard_scrape.json", 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
    else:
        print("Failed to connect.")
