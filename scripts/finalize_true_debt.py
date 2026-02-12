import csv
import json
import os
import re

CSV_FILE = "data/atomic_fund_analysis.csv"
VAULT_FILE = "data/vault_mapping.json"
LEDGER_FILE = "data/internal_ledger.json"
REGISTRY_FILE = "data/campaign_registry.json"
REPORT_FILE = "data/true_debt_report.json"

def clean_phone(p):
    return re.sub(r'\D', '', str(p))

def run_audit():
    # 1. Load data
    with open(VAULT_FILE, 'r', encoding='utf-8') as f:
        vault = json.load(f)
    
    with open(LEDGER_FILE, 'r', encoding='utf-8') as f:
        ledger = json.load(f)
        
    registry = {}
    if os.path.exists(REGISTRY_FILE):
        with open(REGISTRY_FILE, 'r', encoding='utf-8') as f:
            registry = json.load(f).get("mappings", {})

    # 2. Build reverse vault mapping (Address -> Normalized ID)
    addr_to_id = {}
    addr_to_original_id = {}
    for chat_id, data in vault.items():
        addr = data.get('address')
        if addr:
            norm_id = clean_phone(chat_id)
            addr_to_id[addr] = norm_id
            addr_to_original_id[addr] = chat_id

    # 3. Build mapping between Registry IDs and Ledger Keys
    norm_id_to_ledger = {}
    for bid, data in registry.items():
        name = data.get('name')
        norm_bid = clean_phone(bid)
        if name and name in ledger:
            norm_id_to_ledger[norm_bid] = name

    # 4. Process CSV
    uncoupled_out = []
    uncoupled_in = []
    
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['coupled'] == 'False':
                addr = row['address']
                amount = float(row['amount'])
                norm_id = addr_to_id.get(addr)
                original_id = addr_to_original_id.get(addr)
                
                # Identify Ledger Name
                ledger_name = None
                
                # Choice 1: Via registry mapping
                if norm_id and norm_id in norm_id_to_ledger:
                    ledger_name = norm_id_to_ledger[norm_id]
                
                # Choice 2: Direct name match in vault
                if not ledger_name and original_id in ledger:
                    ledger_name = original_id
                
                # Choice 3: BID match
                if not ledger_name and original_id in registry:
                    reg_name = registry[original_id].get('name')
                    if reg_name in ledger:
                        ledger_name = reg_name

                entry = {
                    "date": row['date'],
                    "amount": amount,
                    "address": addr,
                    "id": original_id or "Unknown",
                    "ledger_name": ledger_name,
                    "txid": row['txid']
                }
                
                if row['type'] == 'OUT':
                    uncoupled_out.append(entry)
                else:
                    uncoupled_in.append(entry)

    # 5. Aggregate by Ledger Name
    debt_adjustments = {}
    for entry in uncoupled_out:
        name = entry['ledger_name'] or "Orphan"
        if name not in debt_adjustments:
            debt_adjustments[name] = {"payouts": 0, "redonations": 0}
        debt_adjustments[name]["payouts"] += entry["amount"]

    for entry in uncoupled_in:
        name = entry['ledger_name'] or "Orphan"
        if name not in debt_adjustments:
            debt_adjustments[name] = {"payouts": 0, "redonations": 0}
        debt_adjustments[name]["redonations"] += entry["amount"]

    # 6. Generate True Debt Report
    report = {
        "summary": {
            "total_uncoupled_out": sum(e['amount'] for e in uncoupled_out),
            "total_uncoupled_in": sum(e['amount'] for e in uncoupled_in),
            "net_unreconciled": sum(e['amount'] for e in uncoupled_out) - sum(e['amount'] for e in uncoupled_in),
            "mapped_payouts": sum(e['amount'] for e in uncoupled_out if e['ledger_name']),
            "orphan_payouts": sum(e['amount'] for e in uncoupled_out if not e['ledger_name'])
        },
        "by_account": {}
    }

    for name, data in ledger.items():
        adj = debt_adjustments.get(name, {"payouts": 0, "redonations": 0})
        balance = data.get("unpaid_balance_eur", 0)
        true_debt = balance - adj["payouts"] + adj["redonations"]
        
        report["by_account"][name] = {
            "ledger_balance": balance,
            "unreconciled_payouts": adj["payouts"],
            "unreconciled_redonations": adj["redonations"],
            "true_debt": round(true_debt, 2)
        }

    # Add Orphans
    if "Orphan" in debt_adjustments:
        report["by_account"]["Orphan"] = debt_adjustments["Orphan"]

    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print(f"Audit Complete. Report generated: {REPORT_FILE}")
    print(f"Mapped Payouts: {report['summary']['mapped_payouts']}")
    print(f"Orphan Payouts: {report['summary']['orphan_payouts']}")

if __name__ == "__main__":
    run_audit()
