import json

try:
    with open('data/binance_funded_trustees.json', 'r') as f:
        data = json.load(f)
        
    lines = []
    lines.append(f"Summary of Historical Trustee Funding from Binance Primary Sources (Since Jan 2024):\n")
    lines.append(f"{'Trustee TRC20 Address'.ljust(36)} | {'Total USDT'.rjust(12)} | {'Tx Count'.rjust(10)}")
    lines.append("-" * 65)
    
    total_usdt = 0
    total_txs = 0
    
    # Sort by amount descending
    sorted_items = sorted(data.items(), key=lambda x: sum(t['amount'] for t in x[1]), reverse=True)
    
    for addr, txs in sorted_items:
        addr_total = sum(t['amount'] for t in txs)
        total_usdt += addr_total
        total_txs += len(txs)
        
        lines.append(f"{addr.ljust(36)} | {addr_total:12.2f} | {len(txs):10}")
        
    lines.append("-" * 65)
    lines.append(f"{'GRAND TOTAL'.ljust(36)} | {total_usdt:12.2f} | {total_txs:10}")
    
    with open('data/binance_funding_summary.txt', 'w') as f:
        f.write('\n'.join(lines))
        
    print("Summary written to data/binance_funding_summary.txt")

except Exception as e:
    print(f"Error: {e}")
