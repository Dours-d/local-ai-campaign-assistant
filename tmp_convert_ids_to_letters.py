import os
import glob
import re

def num_to_letters_ag(n):
    res = ''
    while n > 0:
        n -= 1
        res = chr(65 + (n % 7)) + res
        n //= 7
    return res

files = glob.glob('data/dropped_campaigns_ready_for_creation/*.txt')
count = 0

for f in files:
    with open(f, 'r', encoding='utf-8') as text_f:
        content = text_f.read()
    
    m = re.search(r'--- MESSAGE FOR (.*?) ---', content)
    if m:
        current_id = m.group(1).strip()
        
        match_suffix = re.search(r'^(.*?)[-\s_]*0*(\d+)$', current_id)
        if match_suffix:
            base_name = match_suffix.group(1).strip()
            num = int(match_suffix.group(2))
            letter_suffix = num_to_letters_ag(num)
            
            new_id = f'{base_name}{letter_suffix}'
            
            new_content = content.replace(current_id, new_id)
            with open(f, 'w', encoding='utf-8') as out_f:
                out_f.write(new_content)
            print(f"File {os.path.basename(f)}: '{current_id}' -> '{new_id}'")
            count += 1

print(f'Successfully converted {count} IDs to Base-7 (A-G) lettering.')
