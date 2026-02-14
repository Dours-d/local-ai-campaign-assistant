from whydonate_batch_automater import WhyDonateAutomator
import json
import time

def check_dashboard():
    a = WhyDonateAutomator()
    if not a.connect():
        print("Failed to connect")
        return
    
    print("Navigating to Dashboard...")
    a.run_js('window.location.href = "https://whydonate.com/dashboard"')
    time.sleep(12)
    
    a.take_screenshot('data/dash_final_verify.png')
    
    # Try multiple selectors for titles
    titles = a.run_js("""
        (function() {
            const sels = ['mat-card-title', '.mat-mdc-card-title', '.fundraiser-card-title', 'h2', 'h3'];
            let found = [];
            sels.forEach(s => {
                Array.from(document.querySelectorAll(s)).forEach(el => {
                    const txt = el.innerText.trim();
                    if (txt && !found.includes(txt)) found.push(txt);
                });
            });
            return found;
        })()
    """)
    
    print("DASHBOARD_TITLES:")
    print(json.dumps(titles, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    check_dashboard()
