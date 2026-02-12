import csv
import os
import sys

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
TRUST_CSV = os.path.join(DATA_DIR, 'reports', 'trust_health_table.csv')
OUTPUT_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'cell_mapping_template.csv')

def generate_template():
    if not os.path.exists(TRUST_CSV):
        print(f"Error: {TRUST_CSV} not found. Run generate_trust_report.py first.")
        return

    mapping_rows = []
    
    with open(TRUST_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Match new humanized headers
            tid = row.get('Trustee ID', '')
            name = row.get('Name', '')
            effort = row.get('Fundraising Effort', '0')
            solidarity = row.get('Solidarity Contribution / (Gap)', '0')
            share = row.get('Personal Share (Debt)', '0')
            
            # Metrics to map
            metrics = [
                ("Expected Fundraising Effort", effort),
                ("Expected Solidarity Contribution", solidarity),
                ("Expected Personal Share (Debt)", share)
            ]
            
            for metric_name, current_val in metrics:
                mapping_rows.append({
                    "Trustee ID": tid,
                    "Name": name,
                    "Metric": metric_name,
                    "Current Value": current_val,
                    "Cell Address (e.g. Main!B23)": ""
                })

    headers = ["Trustee ID", "Name", "Metric", "Current Value", "Cell Address (e.g. Main!B23)"]
    
    with open(OUTPUT_CSV, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(mapping_rows)

    print(f"Humanized Template generated at: {OUTPUT_CSV}")

if __name__ == "__main__":
    generate_template()
