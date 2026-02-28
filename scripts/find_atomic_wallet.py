import requests
from datetime import datetime

address = "TSVeXzKYfK89Drcw4XHU9XfKQcEzUekipC" # Al-Baz
url = "https://apilist.tronscanapi.com/api/token_trc20/transfers"

params = {
    "limit": 50,
    "start": 0,
    "direction": "in",
    "relatedAddress": address
}

output_lines = []

try:
    res = requests.get(url, params=params).json()
    txs = res.get("token_transfers", [])
    
    for t in txs:
        date_str = datetime.fromtimestamp(t['block_ts']/1000).strftime('%Y-%m-%d %H:%M:%S')
        amt = float(t['quant']) / (10**int(t['tokenInfo']['tokenDecimal']))
        sender = t['from_address']
        output_lines.append(f"[{date_str}] IN | {amt:.2f} USDT | From: {sender}")

except Exception as e:
    output_lines.append(f"Error querying {address}: {e}")

with open('data/atomic_wallet_search.txt', 'w') as f:
    f.write('\n'.join(output_lines))
    
print("Saved search details to data/atomic_wallet_search.txt")
