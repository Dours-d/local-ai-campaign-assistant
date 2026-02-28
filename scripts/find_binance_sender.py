import requests
import json
import time
from collections import Counter

# Known trustee addresses (to be expanded)
TRUSTEES = [
    "TSVeXzKYfK89Drcw4XHU9XfKQcEzUekipC", # Mohamad Al-Baz
    "TDYKY7KDE3Z9mJYovks7aWgMuqCzDaeGST"  # Mahmoud Basem AlkFarna
]

def get_binance_senders(address):
    url = "https://apilist.tronscanapi.com/api/token_trc20/transfers"
    # TRC20 for USDT on TRON
    params = {
        "limit": 50,
        "start": 0,
        "direction": "in",
        "relatedAddress": address
    }
    
    senders = []
    
    try:
        # Get total transfers first to handle pagination
        res = requests.get(url, params={"limit": 1, "direction": "in", "relatedAddress": address}).json()
        total = res.get("total", 0)
        
        # Tronscan limits start to 10000. If more, we can't easily get earliest via this offset method.
        # But for these addresses, total is usually < 1000.
        
        # Paginate through all incoming transactions
        for start in range(0, min(total, 500), 50): # Limiting to 500 for speed
            params["start"] = start
            print(f"  Fetching offset {start} for {address}...")
            res = requests.get(url, params=params).json()
            txs = res.get("token_transfers", [])
            for t in txs:
                if t['to_address'] == address:
                    senders.append(t['from_address'])
            time.sleep(0.5) # Rate limiting
            
    except Exception as e:
        print(f"Error querying {address}: {e}")
        
    return senders

def analyze_senders():
    all_senders = []
    for t in TRUSTEES:
        print(f"Analyzing {t}...")
        senders = get_binance_senders(t)
        all_senders.extend(senders)
        print(f"  Found {len(senders)} incoming transfers.")
        
    # Count frequency of sender addresses
    sender_counts = Counter(all_senders)
    
    print("\n--- Most Frequent Senders to Trustees ---")
    for sender, count in sender_counts.most_common(5):
        print(f"Address: {sender} | Count: {count}")
        
if __name__ == "__main__":
    analyze_senders()
