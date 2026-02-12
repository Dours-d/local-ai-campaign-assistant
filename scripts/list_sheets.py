import re
import os

content_path = 'temp_total2/content.xml'
with open(content_path, 'r', encoding='utf-8', errors='ignore') as f:
    data = f.read()

names = re.findall(r'table:name="(.*?)"', data)
print("Sheet Names:", names)
