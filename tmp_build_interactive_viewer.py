import os
import glob
import webbrowser
import html

in_dir = r"C:\Users\gaelf\Documents\GitHub\local_ai_campaign_assistant\data\dropped_campaigns_ready_for_creation"
out_html = r"C:\Users\gaelf\Documents\GitHub\local_ai_campaign_assistant\campaign_cards_viewer.html"

files = glob.glob(os.path.join(in_dir, "*.txt"))

html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Campaign Cards Interactive Viewer</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #111; color: #eee; margin: 0; padding: 20px; }
        .container { max-width: 800px; margin: auto; }
        h1 { text-align: center; color: #4ade80; }
        .card { background: #222; border: 1px solid #333; border-radius: 10px; margin-bottom: 30px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        .card img { max-width: 100%; border-radius: 5px; margin-top: 10px; }
        .content { white-space: pre-wrap; font-family: monospace; background: #000; padding: 15px; border-radius: 5px; color: #a3e635; margin-top: 15px; overflow-x: auto;}
        .tools { margin-top: 15px; background: #1a1a1a; padding: 15px; border-radius: 5px; border: 1px dashed #444; display: flex; flex-direction: column; gap: 10px;}
        input[type="text"] { width: 100%; padding: 12px; border-radius: 5px; border: 1px solid #555; background: #000; color: #fff; font-size: 16px; box-sizing: border-box; }
        input[type="text"]:focus { border-color: #4ade80; outline: none; }
        .btn { background: #4ade80; color: #000; border: none; padding: 12px 20px; cursor: pointer; border-radius: 5px; font-weight: bold; font-size: 14px; text-transform: uppercase; transition: background 0.2s; align-self: flex-start;}
        .btn:hover { background: #22c55e; }
        .btn:active { background: #16a34a; }
        .toast { position: fixed; top: 20px; right: 20px; background: #4ade80; color: #000; padding: 15px 25px; border-radius: 5px; font-weight: bold; display: none; z-index: 1000; box-shadow: 0 4px 6px rgba(0,0,0,0.3); font-size: 16px;}
    </style>
</head>
<body>
    <div id="toast" class="toast">✔️ Message copied to clipboard!</div>
    <div class="container">
        <h1>Campaign Cards Interactive Viewer</h1>
        <p style="text-align: center; color: #aaa; margin-bottom: 40px; font-size: 1.1em;">
            Paste the created WhyDonate URL in the text box for each campaign.<br>
            It will automatically update the placeholder in the message and let you copy it instantly.
        </p>
"""

for i, f in enumerate(files):
    with open(f, "r", encoding="utf-8", errors="replace") as inf:
        text = inf.read().replace("", "")
        
    img_line = [l for l in text.splitlines() if "**Local File Path:** `" in l]
    img_path = None
    if img_line:
        parts = img_line[0].split("`")
        if len(parts) > 1:
            path = parts[1]
            if os.path.exists(path):
                img_path = path

    id_safe = os.path.basename(f).replace(".txt", "")
    
    html_content += f'<div class="card" id="card_{id_safe}">\n'
    html_content += f'<h2 style="margin-top:0; border-bottom: 1px solid #444; padding-bottom: 10px;">ID: {id_safe}</h2>\n'
    if img_path:
        html_content += f'<img src="file:///{img_path.replace(chr(92), "/")}" alt="Campaign Image">\n'
        
    html_content += f'''
        <div class="tools">
            <label for="link_{id_safe}" style="font-weight: bold; color: #4ade80;">🔗 Paste WhyDonate Link:</label>
            <input type="text" id="link_{id_safe}" placeholder="https://whydonate.com/..." oninput="updateMessage('{id_safe}')">
            <button class="btn" onclick="copyMessage('{id_safe}')">📋 Copy Bilingual Message</button>
        </div>
        <div class="content" id="content_{id_safe}">{html.escape(text)}</div>
'''
    html_content += '</div>\n'

html_content += """
    </div>
    
    <script>
        // Store original text
        const originalTexts = {};
        document.querySelectorAll('.content').forEach(el => {
            const id = el.id.replace('content_', '');
            // use innerText to preserve linebreaks from the dom appropriately, but we'll use original raw text
            originalTexts[id] = el.innerText;
        });
        
        function updateMessage(id) {
            const linkInput = document.getElementById('link_' + id).value;
            const contentEl = document.getElementById('content_' + id);
            const original = originalTexts[id];
            
            if (linkInput.trim() !== '') {
                contentEl.innerText = original.replaceAll('[INSERT WHYDONATE LINK HERE]', linkInput.trim());
            } else {
                contentEl.innerText = original;
            }
        }
        
        function copyMessage(id) {
            const contentEl = document.getElementById('content_' + id);
            
            // Extract just the message block
            const text = contentEl.innerText;
            const marker = "--- MESSAGE FOR";
            let toCopy = text;
            
            if (text.includes(marker)) {
                // start copying from the marker line
                toCopy = text.substring(text.indexOf(marker));
            }
            
            navigator.clipboard.writeText(toCopy).then(() => {
                const toast = document.getElementById('toast');
                toast.style.display = 'block';
                setTimeout(() => { toast.style.display = 'none'; }, 2000);
            });
        }
    </script>
</body>
</html>
"""

with open(out_html, "w", encoding="utf-8") as outf:
    outf.write(html_content)

print("Generated Interactive HTML Viewer at:", out_html)
webbrowser.open(f"file:///{out_html.replace(chr(92), '/')}")
