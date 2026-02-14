from scripts.whydonate_batch_automater import WhyDonateAutomator
import time
import json

def debug_story():
    wa = WhyDonateAutomator()
    wa.connect()
    print("Clicking story container...")
    wa.run_js("const s = document.getElementById('createFundraiserStoryDescription'); if(s) s.click();")
    time.sleep(3)
    inner = wa.run_js("document.body.innerHTML")
    with open('data/debug_story_dom.html', 'w', encoding='utf-8') as f:
        f.write(inner)
    print("DOM saved to data/debug_story_dom.html")

if __name__ == "__main__":
    debug_story()
