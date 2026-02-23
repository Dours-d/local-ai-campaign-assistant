import os
import glob
import shutil

in_dir = r"C:\Users\gaelf\Documents\GitHub\local_ai_campaign_assistant\data\dropped_campaigns_ready_for_creation"
out_file = r"C:\Users\gaelf\.gemini\antigravity\brain\f1ae3bc1-a4b9-4175-ae88-a3cfcc2c7e4c\walkthrough.md"
brain_dir = r"C:\Users\gaelf\.gemini\antigravity\brain\f1ae3bc1-a4b9-4175-ae88-a3cfcc2c7e4c"

files = glob.glob(os.path.join(in_dir, "*.txt"))

with open(out_file, "w", encoding="utf-8") as out:
    out.write("# Collection of Campaign Cards\n\n")
    out.write("Here are all 46 campaign cards that were recently generated. Scroll down to view them all.\n\n")
    
    for i, f in enumerate(files):
        with open(f, "r", encoding="utf-8", errors="replace") as inf:
            text = inf.read()
        
        # Remove any lingering replacement character
        text = text.replace("", "")
            
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
                md_img_path = new_img_path.replace("\\", "/")
                out.write(f"![{filename}](file:///{md_img_path})\n\n")
            except Exception as e:
                pass
                
        out.write("```text\n")
        out.write(text.replace("```", "'''"))
        out.write("\n```\n\n---\n\n")
