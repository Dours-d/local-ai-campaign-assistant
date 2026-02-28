import sys
import requests
from datetime import datetime

def get_oldest(address):
    base_url = "https://apilist.tronscanapi.com/api/token_trc20/transfers"
    # First get the total count
    res = requests.get(base_url, params={"relatedAddress": address, "limit": 1}).json()
    total = res.get("total", 0)
    print(f"Total transfers: {total}")
    
    if total == 0:
        return
        
    # Standard APIs usually limit the 'start' param, but we can try jumping to the end
    # Note: Tronscan API actually limits start to 10000 for public tier.
    # If the address has < 10000 transfers, we can just jump to the last page.
    start = max(0, total - 50)
    print(f"Fetching from offset: {start}")
    
    params = {
        "limit": 50,
        "start": start,
        "relatedAddress": address
    }
    
    res = requests.get(base_url, params=params).json()
    txs = res.get("token_transfers", [])
    if not txs:
        print("No transactions returned at that offset.")
        return
        
    # The API returns newest first, so the items at the end of the last page are the oldest.
    # Reverse to show oldest first.
    txs.reverse()
    
    print("\nEarliest TRC20 Transfers for " + address)
    for t in txs[:10]:
        date_str = datetime.fromtimestamp(t['block_ts']/1000).strftime('%Y-%m-%d %H:%M:%S')
        amt = float(t['quant']) / (10**int(t['tokenInfo']['tokenDecimal']))
        sym = t['tokenInfo']['tokenAbbr']
        direction = "IN " if t['to_address'] == address else "OUT"
        cp = t['from_address'] if direction == "IN " else t['to_address']
        print(f"[{date_str}] {direction} | {amt:.2f} {sym} | Counterparty: {cp}")

if __name__ == "__main__":
    get_oldest(sys.argv[1] if len(sys.argv) > 1 else 'TDYKY7KDE3Z9mJYovks7aWgMuqCzDaeGST')
