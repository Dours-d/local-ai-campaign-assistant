import json
import os
from pathlib import Path

def analyze_discarded():
    dir_path = Path('data/onboarding_submissions')
    discarded_files = [f for f in dir_path.glob('*_submission.json') if any(x in f.name for x in ['viral_', 'test_', 'MOCK', 'myself'])]
    
    report = []
    for f in discarded_files:
        try:
            with open(f, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            report.append({
                "Filename": f.name,
                "Title": data.get('title', 'N/A')[:100],
                "Phone": data.get('whatsapp_number', 'N/A'),
                "Goal": data.get('goal', 'N/A'),
                "Description_Snippet": data.get('description', 'N/A')[:100].replace('\n', ' ')
            })
        except Exception as e:
            report.append({"Filename": f.name, "Error": str(e)})
            
    # Sort by filename
    report.sort(key=lambda x: x['Filename'])
    
    with open('data/discarded_submissions_report.json', 'w', encoding='utf-8') as out:
        json.dump(report, out, indent=2, ensure_ascii=False)
    
    print(f"Analyzed {len(report)} discarded files. Results in data/discarded_submissions_report.json")

if __name__ == "__main__":
    analyze_discarded()
