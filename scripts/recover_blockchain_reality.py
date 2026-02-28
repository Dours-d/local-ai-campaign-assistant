import os
import re
import json
import csv

# Paths
EXPORTS_DIR = "data/exports"
ATOMIC_LOG = "data/atomic_wallet_log/history-atomicwallet-02.02.2026.csv"
LEDGER_FILE = "data/internal_ledger.json"
OUTPUT_MAPPING = "data/atomic_reality_mapping.json"

# Patterns
TRC20_PATTERN = re.compile(r'T[A-Za-z0-9]{33}')

def recover():
    print("Starting Blockchain Reality Recovery...")
    
    # 1. Load Ledger Keys for matching
    with open(LEDGER_FILE, 'r', encoding='utf-8') as f:
        ledger = json.load(f)
        ledger_keys = list(ledger.keys())

    # 2. Scan Exports for TRC20 and attribute to filenames
    # Filename -> [Addresses]
    file_to_addr = {}
    
    for filename in os.listdir(EXPORTS_DIR):
        filepath = os.path.join(EXPORTS_DIR, filename)
        if os.path.isdir(filepath): continue
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                matches = TRC20_PATTERN.findall(content)
                if matches:
                    file_to_addr[filename] = list(set(matches))
        except Exception as e:
            print(f"Error reading {filename}: {e}")

    # 3. Map filenames/IDs to Ledger Keys
    # Address -> [LedgerKey]
    addr_to_key = {}
    for filename, addresses in file_to_addr.items():
        matched_key = None
        
        # Try finding key in filename
        for key in ledger_keys:
            if key.lower() in filename.lower():
                matched_key = key
                break
        
        if matched_key:
            for addr in addresses:
                if addr not in addr_to_key: addr_to_key[addr] = []
                if matched_key not in addr_to_key[addr]:
                    addr_to_key[addr].append(matched_key)

    print(f"Identified {len(addr_to_key)} unique addresses associated with ledger keys.")

    # 4. Cross-reference with Atomic History
    # Transaction ID -> { LedgerKey, Amount, Date, Address }
    atomic_reality = []
    
    if os.path.exists(ATOMIC_LOG):
        with open(ATOMIC_LOG, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('OUTCURRENCY') == 'TRX-USDT':
                    addr = row.get('ADDRESSTO')
                    if addr in addr_to_key:
                        amount = float(row.get('OUTAMOUNT', 0))
                        txid = row.get('ORDERID') or row.get('INTXID')
                        date = row.get('DATE')
                        
                        for key in addr_to_key[addr]:
                            atomic_reality.append({
                                "ledger_key": key,
                                "amount_usdt": amount,
                                "date": date,
                                "address": addr,
                                "txid": txid
                            })

    # 5. Save results
    with open(OUTPUT_MAPPING, 'w', encoding='utf-8') as f:
        json.dump({
            "address_attribution": addr_to_key,
            "verified_transactions": atomic_reality
        }, f, indent=2)

    print(f"Recovery complete. Found {len(atomic_reality)} verified blockchain payouts.")
    total_usdt = sum(tx['amount_usdt'] for tx in atomic_reality)
    print(f"Total Atomic Reality Value: {total_usdt:.2f} USDT")

if __name__ == "__main__":
    recover()
