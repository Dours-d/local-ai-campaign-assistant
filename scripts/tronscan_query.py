import sys
import requests
from datetime import datetime

def query_oldest_trc20(address):
    url = f"https://apilist.tronscanapi.com/api/token_trc20/transfers"
    params = {
        "limit": 50,
        "start": 0,
        "sort": "timestamp", # Ascending order to get oldest first
        "count": "true",
        "relatedAddress": address
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    try:
        print(f"Querying Tronscan API for: {address}")
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        transfers = data.get("token_transfers", [])
        if not transfers:
            print("No TRC20 transfers found for this address.")
            return

        print(f"Total TRC20 transfers registered: {data.get('total')}")
        print("\nEarliest TRC20 Transfers (Oldest First):")
        for t in transfers[:10]:
            date_str = datetime.fromtimestamp(t['block_ts'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
            amount = float(t['quant']) / (10 ** int(t['tokenInfo']['tokenDecimal']))
            token = t['tokenInfo']['tokenAbbr']
            direction = "IN " if t['to_address'] == address else "OUT"
            counterparty = t['from_address'] if direction == "IN " else t['to_address']
            
            print(f"[{date_str}] {direction} | Amount: {amount} {token} | Counterparty: {counterparty}")
            
    except Exception as e:
        print(f"Failed to query Tronscan API: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        query_oldest_trc20(sys.argv[1])
    else:
        print("Usage: python tronscan_query.py <TRON_ADDRESS>")
