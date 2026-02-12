import re

def extract_rows(file_path, targets):
    current_sheet = None
    results = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if '--- VISUALIZING' in line:
                current_sheet = re.search(r'--- VISUALIZING (.*?) \(', line).group(1).strip()
                continue
            
            if current_sheet in targets:
                row_targets = targets[current_sheet]
                for rt in row_targets:
                    if f'Row {rt}:' in line:
                        if (current_sheet, rt) not in results:
                            results[(current_sheet, rt)] = line.strip()
    return results

targets = {
    'Rania': [164],
    'Ibtisam': [410],
    'Fayez': [895],
    'Let\'s draw a smile (Ahmed\'s daughter)': [21],
    'Mahmoud Basem': [492],
    'Mohammed  Suhail': [111],
    'Samirah': [350],
}

extracted = extract_rows('sheet_viz_final_audit.txt', targets)
for (s, r), val in extracted.items():
    print(f'SHEET: {s} | ROW: {r} | CONTENT: {val}')

print("\n--- SEARCHING FOR 5536 IN RANIA SHEET ---")
in_rania = False
with open('sheet_viz_final_audit.txt', 'r', encoding='utf-8') as f:
    for line in f:
        if '--- VISUALIZING Rania' in line:
            in_rania = True
            continue
        if in_rania and '--- VISUALIZING' in line:
            break
        if in_rania and '5536' in line:
            print(line.strip())
