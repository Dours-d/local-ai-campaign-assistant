import json
from collections import Counter
import requests
import time

trustees = [
    'TSVeXzKYfK89Drcw4XHU9XfKQcEzUekipC', # Mohamad Al-Baz
    'TDYKY7KDE3Z9mJYovks7aWgMuqCzDaeGST'  # Mahmoud Basem AlkFarna
]

all_senders = []
url = 'https://apilist.tronscanapi.com/api/token_trc20/transfers'

for addr in trustees:
    print(f"Fetching for {addr}...")
    try:
        res = requests.get(url, params={'relatedAddress': addr, 'limit': 50, 'direction': 'in'}).json()
        txs = res.get('token_transfers', [])
        all_senders.extend([t['from_address'] for t in txs])
    except Exception as e:
        print(f"Error fetching {addr}: {e}")
    time.sleep(0.5)

counts = Counter(all_senders)
most_common = counts.most_common(10)

output_data = [{"address": k, "count": v} for k, v in most_common]

with open('data/binance_senders.json', 'w') as f:
    json.dump(output_data, f, indent=2)

print("Saved top senders to data/binance_senders.json")
