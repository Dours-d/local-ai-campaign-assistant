import re
import os

content_path = 'temp_total2/content.xml'
with open(content_path, 'r', encoding='utf-8', errors='ignore') as f:
    data = f.read()

print("--- SEARCHING FOR '5536.12' ---")
for m in re.finditer(r'5536\.12|5536,12', data):
    print(f"Found at {m.start()}")
    print(f"Context: {data[max(0, m.start()-200):m.end()+200]}")

print("\n--- DUMPING ALL ANNOTATIONS ---")
for m in re.finditer(r'<office:annotation.*?</office:annotation>', data, re.DOTALL):
    ann_xml = m.group(0)
    # Get sheet name
    table_name_match = re.findall(r'table:name="(.*?)"', data[:m.start()])
    table_name = table_name_match[-1] if table_name_match else "Unknown"
    
    # Get text
    p_texts = re.findall(r'<text:p>(.*?)</text:p>', ann_xml)
    ann_text = " | ".join(p_texts)
    
    # Get cell context (walk back to previous cell start)
    cell_context = data[max(0, m.start()-500):m.start()]
    
    if any(x in ann_text.lower() for x in ['rania', 'ibtisam', 'fayez', 'debt', 'gross', '5536']):
         print(f"Sheet: {sheet} | Text: {ann_text}")
         print(f"Cell Context: {cell_context[-300:]}")
         print("-" * 50)

# Also dump ALL annotations mentioning Rania, Ibtisam, Fayez regardless of cell
print("\n--- ANY ANNOTATION MENTIONING TARGET NAMES ---")
for m in re.finditer(r'<office:annotation.*?</office:annotation>', data, re.DOTALL):
    ann_xml = m.group(0)
    p_texts = re.findall(r'<text:p>(.*?)</text:p>', ann_xml)
    ann_text = " | ".join(p_texts)
    if any(x in ann_text.lower() for x in ['rania', 'ibtisam', 'fayez']):
        table_name_match = re.findall(r'table:name="(.*?)"', data[:m.start()])
        sheet = table_name_match[-1] if table_name_match else "Unknown"
        print(f"Sheet: {sheet} | Comment: {ann_text}")
