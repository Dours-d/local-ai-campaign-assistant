import re

def filter_main_sheet(file_path):
    in_main = False
    results = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if '--- VISUALIZING Main' in line:
                in_main = True
                continue
            if in_main and '--- VISUALIZING' in line:
                break
            
            if in_main:
                if any(k in line.lower() for k in ["mahmod", "mahmoud", "bassem", "rebuild"]):
                    results.append(line.strip())
    
    return results

results = filter_main_sheet('sheet_viz_results_v5.txt')
for r in results:
    print(r)
