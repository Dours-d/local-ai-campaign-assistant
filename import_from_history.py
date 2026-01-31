import csv
import json
import os
from datetime import datetime
from src.utils.currency_converter import CurrencyConverter

def extract_campaigns(csv_path):
    campaigns = {}
    
    if not os.path.exists(csv_path):
        return []

    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = row.get('Description', '').strip()
            if not title or title.lower() in ['system', 'test', 'payment']:
                continue
            
            amount = float(row.get('Amount', 0))
            currency = row.get('Currency', 'EUR')
            
            if title not in campaigns:
                campaigns[title] = {
                    "project_title": title,
                    "total_raised_eur": 0.0,
                    "donations_count": 0,
                    "last_donation": row.get('Created At')
                }
            
            if row.get('Type', '').lower() == 'donation':
                amount_eur = CurrencyConverter.convert_to_eur(amount, currency)
                campaigns[title]["total_raised_eur"] += amount_eur
                campaigns[title]["donations_count"] += 1
                
    return list(campaigns.values())

if __name__ == "__main__":
    data = extract_campaigns("primary_campaign_dataset.csv")
    with open("whydonate_campaigns.json", "w", encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f"Imported {len(data)} campaigns from transaction history.")
