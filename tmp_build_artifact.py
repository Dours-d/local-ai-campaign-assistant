import os
import glob
import shutil

in_dir = r"C:\Users\gaelf\Documents\GitHub\local_ai_campaign_assistant\data\dropped_campaigns_ready_for_creation"
out_file = r"C:\Users\gaelf\.gemini\antigravity\brain\f1ae3bc1-a4b9-4175-ae88-a3cfcc2c7e4c\walkthrough.md"
brain_dir = r"C:\Users\gaelf\.gemini\antigravity\brain\f1ae3bc1-a4b9-4175-ae88-a3cfcc2c7e4c"

files = glob.glob(os.path.join(in_dir, "*.txt"))

with open(out_file, "w", encoding="utf-8") as out:
    out.write("# Collection of Campaign Cards\n\n")
    out.write("Here are all 46 campaign cards that were recently generated, conveniently accessible on your screen. Swipe or click through the slides below.\n\n")
    out.write("````carousel\n")
    
    for i, f in enumerate(files):
        with open(f, "r", encoding="utf-8") as inf:
            text = inf.read()
            
        img_line = [l for l in text.splitlines() if "**Local File Path:** `" in l]
        img_path = None
        if img_line:
            parts = img_line[0].split("`")
            if len(parts) > 1:
                path = parts[1]
                if os.path.exists(path):
                    img_path = path

        if img_path:
            filename = os.path.basename(img_path)
            new_img_path = os.path.join(brain_dir, filename)
            try:
                shutil.copy2(img_path, new_img_path)
                # Ensure path has forward slashes for markdown to be safe
                md_img_path = new_img_path.replace("\\", "/")
                out.write(f"![{filename}]({md_img_path})\n\n")
            except Exception as e:
                pass
                
        out.write("```text\n")
        out.write(text.replace("```", "'''"))
        out.write("\n```\n")
        
        if i < len(files) - 1:
            out.write("<!-- slide -->\n")
            
    out.write("````\n")
