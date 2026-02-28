import requests
import json

senders = [
    "TPv76s4smSzmMUiU9pYoM9MPNLZCeCYN7e",
    "TU4vEruvZwLLkSfV9bNw12EJTPvNr7Pvaa",
    "TDtNBtCBVWe8kxkjDZiFtXdYkqXBi8ri3J",
    "TGD1EKN4XuZ6B3qJKZovUEaxpoXnUy6bHd",
    "TZ8Ksz21Hk1tQuztCKCUJBRXStCav9uyjM",
    "TCu7Y8HFLbMFCbeTcZdPcte6ZekZdSobc6",
    "TJ7hhYhVhaxNx6BPyq7yFpqZrQULL3JSdb",
    "THqmZqgoSR6RUZwYgUVajMi24Y26CrVoRA",
    "TFDXzPd94CWxxPo5VV1RdHdBcPP7ZoR4wJ",
    "TEPSrSYPDSQ7yXpMFPq91Fb1QEWpMkRGfn",
    "TREysTVRxEAHD4269SpUZzLHt2QFM2G9on",
    "TSfDG39Docf9tYv7HbjaMCBtFnKQ3hF8rt",
    "TEVLmta44bJc1omHGZtWxVCshsNTqFvcZs",
    "TNRqc9usbcdvDdJ1JWxkWCs41CX4PVafz4",
    "TMMxHiw32TpXudHtFVwRXBNreZsgQhA1Wd",
    "TKmC6fFyothgcCbgfYZeawjGCVfA5gDcD2",
    "TGykDbkaRseAezdwz4B5p3U8L3b6EGxBGR",
    "TCNwxoxTzm7Gt4eNPTUQx6GuoDZEDn1QH4",
    "TMV8gL5ZwphpAvjtWWdvLHsiM4pNa54ENz",
    "TNLuUvGo3rrBbFHiA6sqXP9UisJ7RqFeFt",
    "TARd48fMgGXSrRCkQ1AYE5FBmQm8N8KXh9",
    "TCwQnqmCQbMDjWgRhu8EeV6zt8ag9LA77U",
    "TTnPWQ8hajZKAZjzkUrZx9fb6WGGCSFDY5",
    "TS1RtL9mqPKdkgnSJqUzSNDdevH4HPfgqq",
    "TU1vcUWtGUFhPjvqGLytvYDaksPJMFVhB4",
    "TQ6TL5fhxAMc5hHn9koAGErfia4CsoktFr",
    "TXtp6FhA3NXP2eZehTu3W1CptFjaMECDcJ",
    "TVVnbEPBHskuTCKnrR6VycNAiawydM5Ega"
]

url = "https://apilist.tronscanapi.com/api/token_trc20/transfers"
personal_wallets = []

for s in senders:
    try:
        res = requests.get(url, params={"relatedAddress": s, "limit": 1}).json()
        total = res.get("total", 0)
        
        if total < 10000: # Definitive personal wallet threshold
            personal_wallets.append({"address": s, "total_txs": total})
    except Exception as e:
        pass

with open('data/atomic_wallet_candidates.json', 'w') as f:
    json.dump(personal_wallets, f, indent=2)
