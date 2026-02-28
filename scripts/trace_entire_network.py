import requests
import json
import csv
from datetime import datetime

BINANCE_SOURCES = [
    "TPv76s4smSzmMUiU9pYoM9MPNLZCeCYN7e",
    "TU4vEruvZwLLkSfV9bNw12EJTPvNr7Pvaa",
    "TDtNBtCBVWe8kxkjDZiFtXdYkqXBi8ri3J",
    "THqmZqgoSR6RUZwYgUVajMi24Y26CrVoRA",
    "TFDXzPd94CWxxPo5VV1RdHdBcPP7ZoR4wJ",
    "TEPSrSYPDSQ7yXpMFPq91Fb1QEWpMkRGfn",
    "TJMnPF3C4r3nE3vbcn3D9xpJtMaHJLTqyL",
    "TNDB3qe9GbsBvyuwHiDo7Vs2NBxxtq5iFu",
    "TByF623Z3J64oSRZgLDdjKj8LJR296xpA2"
]

url = "https://apilist.tronscanapi.com/api/token_trc20/transfers"

addresses = []
with open('data/pfd_address_mapping.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        addr = row['address'].strip()
        if len(addr) == 34 and addr.startswith('T'):
            addresses.append(addr)
addresses = list(set(addresses))

funded_by_binance = {}
all_senders = {}

# 1. Trace which addresses were funded by the Binance sources
for addr in addresses:
    try:
        res = requests.get(url, params={"relatedAddress": addr, "limit": 200, "direction": "in"}).json()
        txs = res.get("token_transfers", [])
        
        binance_txs = []
        non_binance_senders = set()
        
        for t in txs:
            sender = t['from_address']
            ts = t['block_ts'] / 1000
            
            if ts >= 1704067200: # Epoch for Jan 1 2024
                amt = float(t['quant']) / (10**int(t['tokenInfo']['tokenDecimal']))
                
                if sender in BINANCE_SOURCES:
                    binance_txs.append({"date": datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'), "amount": amt, "source": sender})
                else:
                    non_binance_senders.add(sender)
                    
        if binance_txs:
            funded_by_binance[addr] = binance_txs
            
        all_senders[addr] = non_binance_senders
        
    except Exception as e:
        pass

# Save Binance funded map
with open('data/binance_funded_trustees.json', 'w') as f:
    json.dump(funded_by_binance, f, indent=2)

# 2. Triangulate Atomic Wallet
sender_counts = {}
for addr, senders in all_senders.items():
    for s in senders:
        sender_counts[s] = sender_counts.get(s, 0) + 1
        
potential_atomic = [s for s, count in sender_counts.items() if count > 1]

atomic_candidates = []
for s in potential_atomic:
    try:
        res = requests.get(url, params={"relatedAddress": s, "limit": 1}).json()
        total = res.get("total", 0)
        if total < 5000:
            atomic_candidates.append({"address": s, "total_txs": total, "funded_count": sender_counts[s]})
    except Exception:
        pass

with open('data/triangulated_atomic_candidates.json', 'w') as f:
    json.dump(atomic_candidates, f, indent=2)
    
print("Saved outputs to data/binance_funded_trustees.json and data/triangulated_atomic_candidates.json")
