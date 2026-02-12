import re
import os
import html

content_path = 'temp_total2/content.xml'
with open(content_path, 'r', encoding='utf-8', errors='ignore') as f:
    data = f.read()

def get_ann_text(xml_block):
    if not xml_block: return ""
    # Simplified extraction
    p_texts = re.findall(r'<text:p>(.*?)</text:p>', xml_block)
    return " | ".join(p_texts)

print("--- ALL ANNOTATIONS DUMP ---")
# Find all annotations
# Note: we need to know which sheet they belong to.
# We can find all table:table starts and their ends.

for tbl_match in re.finditer(r'<table:table table:name="(.*?)"', data):
    sheet_name = tbl_match.group(1)
    tbl_start = tbl_match.start()
    tbl_end = data.find('</table:table>', tbl_start)
    sheet_xml = data[tbl_start:tbl_end]
    
    if '<office:annotation' in sheet_xml:
        anns = re.findall(r'<office:annotation.*?</office:annotation>', sheet_xml, re.DOTALL)
        for ann in anns:
            text = get_ann_text(ann)
            # Find the cell value if possible (it's usually in the same cell tag)
            # This is hard because the annotation is inside the cell.
            # Let's find the closing tag of the cell it's in.
            
            # Print sheet and text
            print(f"Sheet: {sheet_name} | Comment: {text}")

print("\n--- SEARCHING FOR TARGET FIGURES ---")
for fig in ['5536.12', '5536,12', '43735', '143387']:
    if fig in data:
        print(f"Figure {fig} found in XML.")
        idx = data.find(fig)
        # Find sheet name
        prev_sheet_match = re.findall(r'table:name="(.*?)"', data[:idx])
        sheet = prev_sheet_match[-1] if prev_sheet_match else "Unknown"
        print(f" Context: {data[max(0, idx-100):idx+100]}")
        print(f" Sheet context: {sheet}")
        print("-" * 30)

# Check "Let's draw a smile" specifically for AB21
print("\n--- CHECKING AHMED SPECIFICALLY ---")
ahmed_pattern = "Let.s draw a smile"
match = re.search(f'table:name="([^"]*{ahmed_pattern}[^"]*)"', data, re.IGNORECASE)
if match:
    sheet_name = match.group(1)
    print(f"Ahmed sheet found: {sheet_name}")
    # Extract AB21
    # ... use the logic from before ...
