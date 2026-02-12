import re

def search_mahmod(file_path):
    in_main = False
    matches = []
    # Flexible on spaces between Mahmod and rebuild
    pattern = re.compile(r'Help Mahmod\s+rebuild his life and support his family in Gaza', re.IGNORECASE)
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if '--- VISUALIZING Main' in line:
                in_main = True
                continue
            if in_main and '--- VISUALIZING' in line:
                break
            if in_main and pattern.search(line):
                matches.append(line.strip())
    
    print(f"Found {len(matches)} lines for 'Help Mahmod rebuild...' in Main")
    for m in matches[:20]:
        # Extract the column values to verify payment status
        print(m)

if __name__ == "__main__":
    search_mahmod('sheet_viz_final_audit.txt')
