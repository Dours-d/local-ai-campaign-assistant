import re

def dump_row(file_path, sheet_name, row_target):
    in_sheet = False
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if f'--- VISUALIZING {sheet_name}' in line:
                in_sheet = True
                continue
            if in_sheet and '--- VISUALIZING' in line:
                break
            if in_sheet and f'Row {row_target}:' in line:
                print(f"SHEET: {sheet_name} | {line.strip()}")
                return
    print(f'Row {row_target} in {sheet_name} NOT FOUND')

targets = [
    ('Ibtisam', 410),
    ('Samirah', 350),
    ('Let\'s draw a smile (Ahmed\'s daughter)', 21),
    ('Rania', 164),
    ('Mahmoud Basem', 492),
    ('Mohammed  Suhail', 111),
]

for s, r in targets:
    dump_row('sheet_viz_final_audit.txt', s, r)
