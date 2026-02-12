import json
import os
import csv

def normalize_name(name):
    replacements = {
        'Aïsha': 'Aisha',
        'Maomé': 'Maome'
    }
    return replacements.get(name, name)

def update_json_list(file_path, list_key, internal_name_path):
    if not os.path.exists(file_path): 
        print(f"Skipping {file_path}, not found.")
        return
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    count = 0
    for item in data.get(list_key, []):
        # Handle nested paths like ['privacy', 'internal_name']
        target = item
        for p in internal_name_path[:-1]:
            target = target.get(p, {})
        
        old_name = target.get(internal_name_path[-1])
        new_name = normalize_name(old_name)
        if old_name != new_name:
            target[internal_name_path[-1]] = new_name
            count += 1
            
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Updated {count} entries in {file_path}")

def update_json_keys(file_path):
    if not os.path.exists(file_path):
        print(f"Skipping {file_path}, not found.")
        return
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    new_data = {}
    count = 0
    for k, v in data.items():
        new_k = normalize_name(k)
        if k != new_k:
            count += 1
        new_data[new_k] = v
        
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, indent=2, ensure_ascii=False)
    print(f"Updated {count} keys in {file_path}")

if __name__ == "__main__":
    # 1. Unified DB
    update_json_list('data/campaigns_unified.json', 'campaigns', ['privacy', 'internal_name'])
    
    # 2. Internal Ledger
    update_json_keys('data/internal_ledger.json')
    
    # 3. Potential Beneficiaries
    pb_path = 'data/potential_beneficiaries.json'
    if os.path.exists(pb_path):
        with open(pb_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        count = 0
        target_list = data if isinstance(data, list) else data.get('beneficiaries', [])
        for item in target_list:
            old = item.get('internal_name')
            new = normalize_name(old)
            if old != new:
                item['internal_name'] = new
                count += 1
                
        with open(pb_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Updated {count} entries in {pb_path}")

    # 4. CSV Mapping
    csv_path = 'GGF/cell_mapping_template.csv'
    if os.path.exists(csv_path):
        rows = []
        count = 0
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            for row in reader:
                old = row['Name']
                new = normalize_name(old)
                if old != new:
                    row['Name'] = new
                    count += 1
                rows.append(row)
        with open(csv_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"Updated {count} rows in {csv_path}")

    # 5. Update generate_trust_report.py HINT_TO_KEY
    report_script = 'scripts/generate_trust_report.py'
    if os.path.exists(report_script):
        with open(report_script, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if '"Maomé": "Maome"' not in content:
            content = content.replace('"Mahmoud": "Mahmoud-002",', '"Mahmoud": "Mahmoud-002",\n        "Maomé": "Maome",')
            content = content.replace('"Aïsha": "Aïsha"', '"Aïsha": "Aisha"') # Correcting existing
            with open(report_script, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated HINT_TO_KEY in {report_script}")
