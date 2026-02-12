import re

def extract_target_rows(file_path):
    targets = {
        'Rania': 164,
        'Ibtisam': 410,
        'Fayez': 895,
        'Let\'s draw a smile': 21,
        'Mahmoud Bassem': 492,
        'Mahmoud Suhail': 111,
        'Samirah': 350
    }
    
    current_sheet = None
    results = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('--- VISUALIZING'):
                match = re.search(r'--- VISUALIZING (.*?) \(Up to', line)
                if match:
                    current_sheet = match.group(1).strip()
            
            if current_sheet:
                for sheet_key, target_row in targets.items():
                    if sheet_key.lower() in current_sheet.lower() or current_sheet.lower() in sheet_key.lower():
                        if line.startswith(f'Row {target_row}:'):
                            results.append(f"Sheet: {current_sheet} | {line}")
    
    return results

results = extract_target_rows('sheet_viz_results_v4.txt')
for r in results:
    print(r)
