import os
import glob
import webbrowser
import html
import re

in_dir = r"C:\Users\gaelf\Documents\GitHub\local_ai_campaign_assistant\data\dropped_campaigns_ready_for_creation"
list_file = r"C:\Users\gaelf\Documents\GitHub\local_ai_campaign_assistant\data\final_real_growth_list.md"
out_html = r"C:\Users\gaelf\Documents\GitHub\local_ai_campaign_assistant\campaign_cards_viewer.html"

# Extract notes and phone numbers mapped to the IDs
notes_map = {}
try:
    with open(list_file, 'r', encoding='utf-8') as f:
        lines = f.read().splitlines()
        
    in_dropped = False
    for line in lines:
        if line.startswith('## ❌ Dropped'):
            in_dropped = True
            continue
        if in_dropped and line.startswith('- '):
            parts = line[2:].strip().split(maxsplit=1)
            if len(parts) >= 1:
                id_val = parts[0]
                if not id_val.startswith('viral_'):
                    id_val = f'chuffed_{id_val}'
                note = parts[1] if len(parts) > 1 else "No contact info available."
                notes_map[id_val] = note
except Exception as e:
    print("Could not parse notes:", e)

files = glob.glob(os.path.join(in_dir, "*.txt"))

# Build HTML
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
        .contact-box { padding: 12px; border-radius: 5px; margin-bottom: 15px; font-size: 1em; line-height: 1.4;}
        .wa-btn { display: inline-block; background: #25D366; color: #fff; text-decoration: none; padding: 5px 12px; border-radius: 5px; font-weight: bold; margin-left: 10px; font-size: 0.9em; box-shadow: 0 2px 4px rgba(0,0,0,0.2);}
        .wa-btn:hover { background: #1da851; }
        .header-tools { display: flex; justify-content: center; margin-bottom: 30px; gap: 15px; }
        .btn-export { background: #3b82f6; color: white; }
        .btn-export:hover { background: #2563eb; }
        .recorded-badge { margin-left: 10px; color: #4ade80; font-size: 0.9em; display: none; }
    </style>
</head>
<body>
    <div id="toast" class="toast">✔️ Action Successful!</div>
    <div class="container">
        <h1>Campaign Cards Interactive Viewer</h1>
        <p style="text-align: center; color: #aaa; margin-bottom: 20px; font-size: 1.1em;">
            Paste the created WhyDonate URL to update the message dynamically.<br>
            Any links you paste and copy will be automatically recorded to the browser's storage!
        </p>
        
        <div class="header-tools">
            <button class="btn btn-export" onclick="exportLinksJSON()">📥 Export Recorded Links JSON</button>
            <button class="btn btn-export" onclick="exportLinksCSV()">📥 Export Recorded Links CSV</button>
        </div>
"""

skipped_count = 0
rendered_count = 0

for i, f in enumerate(files):
    id_safe = os.path.basename(f).replace(".txt", "")
    note = notes_map.get(id_safe, "No contact info / anchor recorded.")
    
    # RULE 1: Discard if "already on Whydonate"
    if "already on Whydonate" in note or "already on whydonate" in note.lower():
        skipped_count += 1
        continue
        
    rendered_count += 1

    with open(f, "r", encoding="utf-8", errors="replace") as inf:
        text = inf.read().replace("", "")

    # RULE 3: Title formatting for Youssef
    if id_safe == "chuffed_145751":
        text = re.sub(r"## 📝 1\. Campaign Title:\n.*?\n\n", "## 📝 1. Campaign Title:\nHelp Youssef and family survive to see the light of a free Palestine\n\n", text, flags=re.DOTALL)

    img_line = [l for l in text.splitlines() if "**Local File Path:** `" in l]
    img_path = None
    if img_line:
        parts = img_line[0].split("`")
        if len(parts) > 1:
            path = parts[1]
            if os.path.exists(path):
                img_path = path

    phone_match = re.search(r'^(\d{10,15})', note)
    whatsapp_html = ""
    if phone_match:
        number = phone_match.group(1)
        whatsapp_html = f'<a href="https://wa.me/{number}" target="_blank" class="wa-btn">💬 Chat on WhatsApp</a>'
        
    # Visual Highlights for edge cases
    box_style = "background: #333; border-left: 4px solid #3b82f6;"
    if "unknown, demand further name researches" in note or "cannot be identified" in note:
        box_style = "background: #4a0404; border-left: 4px solid #ef4444; color: #fca5a5;"
    elif "onboarded" in note:
        box_style = "background: #064e3b; border-left: 4px solid #10b981; color: #a7f3d0;"
    
    html_content += f'<div class="card" id="card_{id_safe}">\n'
    html_content += f'<h2 style="margin-top:0; border-bottom: 1px solid #444; padding-bottom: 10px; display: flex; justify-content: space-between; align-items: center;">ID: {id_safe} <span class="recorded-badge" id="badge_{id_safe}">✔️ Link Recorded</span></h2>\n'
    html_content += f'<div class="contact-box" style="{box_style}"><strong>🚨 Required Action:</strong> {html.escape(note)} {whatsapp_html}</div>\n'
    
    if img_path:
        html_content += f'<img src="file:///{img_path.replace(chr(92), "/")}" alt="Campaign Image">\n'
        
    html_content += f'''
        <div class="tools">
            <label for="link_{id_safe}" style="font-weight: bold; color: #4ade80;">🔗 Paste WhyDonate Link here:</label>
            <input type="text" id="link_{id_safe}" placeholder="https://whydonate.com/..." oninput="updateMessage('{id_safe}')">
            <button class="btn" onclick="copyMessage('{id_safe}')">📋 Copy Bilingual Message & Record Link</button>
        </div>
        <div class="content" id="content_{id_safe}">{html.escape(text)}</div>
'''
    html_content += '</div>\n'


# RULE 2: Manually ADD Magde & Ahmed placeholder campaign
extra_id = "placeholder_magde_ahmed"
extra_phone = "970599157072"
extra_note = 'Explicitly requested blank placeholder campaign for Magde & Ahmed.'
extra_whatsapp_html = f'<a href="https://wa.me/{extra_phone}" target="_blank" class="wa-btn">💬 Chat on WhatsApp</a>'

extra_text = """# Campaign Data Pack: placeholder_magde_ahmed

## 📝 1. Campaign Title:
Magde & Ahmed

## 📖 2. Campaign Story:
> Placeholder text. Please fill in the details manually on WhyDonate.

## 🖼️ 3. Featured Image:
No image available.

======================================================

## 💬 4. Bilingual Onboarding Message
*Copy and send this message to the beneficiary (if found) AFTER creating their WhyDonate campaign.*

--- MESSAGE FOR placeholder_magde_ahmed ---
placeholder_magde_ahmed
السلام عليكم ورحمة الله وبركاته.

حملتكم الآن أمانة (Amanah) مفعلة وجاهزة للنشر! إليك أدواتكم للتمكين:

1️⃣ **رابط النافذة المباشرة (Direct Window)**:
[INSERT WHYDONATE LINK HERE]
استخدموا هذا الرابط لمشاركة قصتكم الشخصية مع العالم وبدء جمع التبرعات مباشرة.

2️⃣ **رابط الدرع الجماعي (مشروع قيد التطوير - Project Status)**:
https://dours-d.github.io/local-ai-campaign-assistant/
هذا الصندوق يضمن كفاءة أعلى وصفر رسوم تحويل. اطلبو من المتبرعين كتابة الـ ID الخاص بكم: **placeholder_magde_ahmed** في الملاحظات.

🌍 **بوابة 'نور' المعرفية**: صمودكم محفوظ الآن في الذاكرة المستقلة للعالم ليكون شهادة للأجيال: https://dours-d.github.io/local-ai-campaign-assistant/brain.html

------------------------------

Salam Alaykum.

Your campaign is now a live Amanah! Use these links to build your support:

1. **Your Direct Window**:
[INSERT WHYDONATE LINK HERE]

2. **The Collective Shield (Project Status - Not Reconciled)**:
https://dours-d.github.io/local-ai-campaign-assistant/
Ask donors to include ID: **placeholder_magde_ahmed** for transparent tracking.

🌍 **Noor Knowledge Portal**: Your story is being safeguarded as a witness for the Ummah: https://dours-d.github.io/local-ai-campaign-assistant/brain.html

------------------------------"""

rendered_count += 1
html_content += f'<div class="card" id="card_{extra_id}">\n'
html_content += f'<h2 style="margin-top:0; border-bottom: 1px solid #444; padding-bottom: 10px; display: flex; justify-content: space-between; align-items: center;">ID: {extra_id} <span class="recorded-badge" id="badge_{extra_id}">✔️ Link Recorded</span></h2>\n'
html_content += f'<div class="contact-box" style="background: #3b0764; border-left: 4px solid #a855f7; color: #e9d5ff;"><strong>🚨 Required Action:</strong> {html.escape(extra_note)} {extra_whatsapp_html}</div>\n'
html_content += f'''
    <div class="tools">
        <label for="link_{extra_id}" style="font-weight: bold; color: #4ade80;">🔗 Paste WhyDonate Link here:</label>
        <input type="text" id="link_{extra_id}" placeholder="https://whydonate.com/..." oninput="updateMessage('{extra_id}')">
        <button class="btn" onclick="copyMessage('{extra_id}')">📋 Copy Bilingual Message & Record Link</button>
    </div>
    <div class="content" id="content_{extra_id}">{html.escape(extra_text)}</div>
'''
html_content += '</div>\n'


html_content += """
    </div>
    
    <script>
        const originalTexts = {};
        document.querySelectorAll('.content').forEach(el => {
            const id = el.id.replace('content_', '');
            originalTexts[id] = el.innerText;
        });
        
        // Load saved links on startup
        window.addEventListener('load', () => {
            const savedLinks = JSON.parse(localStorage.getItem('savedCampaignLinks') || '{}');
            for (const id in savedLinks) {
                const inputEl = document.getElementById('link_' + id);
                if (inputEl) {
                    inputEl.value = savedLinks[id];
                    updateMessage(id);
                    document.getElementById('badge_' + id).style.display = 'inline-block';
                }
            }
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
        
        function saveLinkToStorage(id, link) {
            if (!link.trim()) return;
            const savedLinks = JSON.parse(localStorage.getItem('savedCampaignLinks') || '{}');
            savedLinks[id] = link.trim();
            localStorage.setItem('savedCampaignLinks', JSON.stringify(savedLinks));
            document.getElementById('badge_' + id).style.display = 'inline-block';
        }
        
        function copyMessage(id) {
            const contentEl = document.getElementById('content_' + id);
            const text = contentEl.innerText;
            const linkInput = document.getElementById('link_' + id).value;
            
            const marker = "--- MESSAGE FOR";
            let toCopy = text;
            if (text.includes(marker)) {
                toCopy = text.substring(text.indexOf(marker));
            }
            
            navigator.clipboard.writeText(toCopy).then(() => {
                showToast("✔️ Message copied! " + (linkInput.trim() ? "Link recorded." : ""));
                saveLinkToStorage(id, linkInput);
            }).catch(err => {
                showToast("❌ Failed to copy text!");
            });
        }
        
        function showToast(msg) {
            const toast = document.getElementById('toast');
            toast.innerText = msg;
            toast.style.display = 'block';
            setTimeout(() => { toast.style.display = 'none'; }, 3000);
        }
        
        function exportLinksJSON() {
            const savedLinks = localStorage.getItem('savedCampaignLinks') || '{}';
            const blob = new Blob([savedLinks], { type: "application/json" });
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = "recorded_campaign_links.json";
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
        
        function exportLinksCSV() {
            const savedLinks = JSON.parse(localStorage.getItem('savedCampaignLinks') || '{}');
            let csv = "Campaign_ID,WhyDonate_Link\\n";
            for (const id in savedLinks) {
                csv += `"${id}","${savedLinks[id]}"\\n`;
            }
            const blob = new Blob([csv], { type: "text/csv" });
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = "recorded_campaign_links.csv";
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
    </script>
</body>
</html>
"""

with open(out_html, "w", encoding="utf-8") as outf:
    outf.write(html_content)

print(f"Generated Interactive HTML Viewer at: {out_html}")
print(f"Successfully rendered {rendered_count} cards, skipped {skipped_count} that were already on Whydonate.")
webbrowser.open(f"file:///{out_html.replace(chr(92), '/')}")
