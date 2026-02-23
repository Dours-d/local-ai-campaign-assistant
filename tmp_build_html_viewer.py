import os
import glob
import shutil
import webbrowser

in_dir = r"C:\Users\gaelf\Documents\GitHub\local_ai_campaign_assistant\data\dropped_campaigns_ready_for_creation"
out_html = r"C:\Users\gaelf\Documents\GitHub\local_ai_campaign_assistant\campaign_cards_viewer.html"

files = glob.glob(os.path.join(in_dir, "*.txt"))

html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Campaign Cards Viewer</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #111; color: #eee; margin: 0; padding: 20px; }
        .container { max-width: 800px; margin: auto; }
        h1 { text-align: center; color: #4ade80; }
        .card { background: #222; border: 1px solid #333; border-radius: 10px; margin-bottom: 30px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        .card img { max-width: 100%; border-radius: 5px; margin-top: 10px; }
        .content { white-space: pre-wrap; font-family: monospace; background: #000; padding: 15px; border-radius: 5px; color: #a3e635; margin-top: 15px; overflow-x: auto;}
    </style>
</head>
<body>
    <div class="container">
        <h1>Campaign Cards Viewer (46 Items)</h1>
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

    html_content += f'<div class="card">\n'
    if img_path:
        html_content += f'<img src="file:///{img_path.replace(chr(92), "/")}" alt="Campaign Image">\n'
    html_content += f'<div class="content">{text}</div>\n'
    html_content += '</div>\n'

html_content += """
    </div>
</body>
</html>
"""

with open(out_html, "w", encoding="utf-8") as outf:
    outf.write(html_content)

print("Generated HTML Viewer at:", out_html)
# Open in default browser
webbrowser.open(f"file:///{out_html.replace(chr(92), '/')}")
