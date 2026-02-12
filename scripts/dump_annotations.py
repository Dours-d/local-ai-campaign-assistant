import re
import os

content_path = 'temp_total2/content.xml'
with open(content_path, 'r', encoding='utf-8', errors='ignore') as f:
    data = f.read()

print("--- ALL ANNOTATIONS ---")
for m in re.finditer(r'<office:annotation.*?</office:annotation>', data, re.DOTALL):
    ann_xml = m.group(0)
    # Get sheet name
    table_name_match = re.findall(r'table:name="(.*?)"', data[:m.start()])
    table_name = table_name_match[-1] if table_name_match else "Unknown"
    
    # Get cell context
    cell_context = data[max(0, m.start()-500):m.start()]
    
    # Extract text
    texts = re.findall(r'<text:p>(.*?)</text:p>', ann_xml)
    ann_text = " | ".join(texts)
    
    print(f"Sheet: {table_name}")
    print(f"Annotation Text: {ann_text}")
    print(f"Cell Context: {cell_context[-300:]}")
    print("-" * 50)
