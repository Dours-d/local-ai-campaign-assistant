import requests
import json

trustees = {
    "Al-Baz": "TSVeXzKYfK89Drcw4XHU9XfKQcEzUekipC",
    "Mahmoud": "TDYKY7KDE3Z9mJYovks7aWgMuqCzDaeGST"
}

url = "https://apilist.tronscanapi.com/api/token_trc20/transfers"

def get_senders(address):
    senders = set()
    try:
        # Just grab the last 200 incoming transactions to find recent senders
        for i in range(0, 200, 50):
            res = requests.get(url, params={"relatedAddress": address, "limit": 50, "start": i, "direction": "in"}).json()
            txs = res.get("token_transfers", [])
            for t in txs:
                senders.add(t['from_address'])
    except Exception as e:
        print(f"Error: {e}")
    return senders

print("Fetching senders...")
senders_al_baz = get_senders(trustees["Al-Baz"])
senders_mahmoud = get_senders(trustees["Mahmoud"])

intersection = senders_al_baz.intersection(senders_mahmoud)
print(f"Found {len(intersection)} common senders.")

print("\nChecking transaction volume of common senders...")
atomic_candidates = []
for s in intersection:
    try:
        res = requests.get(url, params={"relatedAddress": s, "limit": 1}).json()
        total = res.get("total", 0)
        
        if total < 5000: # Definitive personal wallet threshold
            print(f"[*] MATcHED ATOMIC WALLET: {s} (Total TXs: {total})")
            atomic_candidates.append(s)
        else:
            print(f"[Exchange Hub] {s} (Total TXs: {total})")
    except Exception as e:
        pass

with open('data/verified_atomic_wallet.json', 'w') as f:
    json.dump(atomic_candidates, f)
