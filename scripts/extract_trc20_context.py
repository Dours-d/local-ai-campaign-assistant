import os
import re
import json

# Paths
EXPORTS_DIR = "data/exports"
LEDGER_FILE = "data/internal_ledger.json"
OUTPUT_MAPPING = "data/trc20_attribution.json"

# TRC20 Base58 Pattern (starts with T, 34 chars total, no 0,O,I,l)
TRC20_PATTERN = re.compile(r'T[1-9A-HJ-NP-Za-km-z]{33}')

def parse_date(content):
    # Try to find common date patterns in exports
    # Example: "16:06, 1/31/2026" or "12/4/2025" or "12-4-2025"
    # Target date is August 2025 (2025/8)
    match = re.search(r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})', content)
    if match:
        try:
            m = int(match.group(1))
            d = int(match.group(2))
            y = int(match.group(3))
            
            if y < 100: y += 2000
            
            # Simple heuristic for MM/DD vs DD/MM
            if m > 12: # If first part is > 12, it's likely DD/MM
                m, d = d, m
            
            return y, m
        except: pass
    return None, None

def refine_recovery():
    print("Starting High-Precision TRC20 Extraction (Binance Recon Mode)...")
    
    # 1. Load Ledger Keys
    if os.path.exists(LEDGER_FILE):
        with open(LEDGER_FILE, 'r', encoding='utf-8') as f:
            ledger = json.load(f)
            ledger_keys = list(ledger.keys())
    else:
        ledger_keys = []

    # 2. Results storage
    results = {}
    address_recurrence = {} 

    for filename in os.listdir(EXPORTS_DIR):
        filepath = os.path.join(EXPORTS_DIR, filename)
        if not os.path.isfile(filepath): continue
        if filename.endswith(".html"): continue 
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                # Skip the exporter script itself
                if "WhatsApp Business Chat Exporter" in content[:1000] or "param (" in content[:500]:
                    continue
                
                year, month = parse_date(content)
                
                # Check for "Blowup" period
                is_pre_aug_2025 = False
                if year and year < 2025: is_pre_aug_2025 = True
                elif year == 2025 and month < 8: is_pre_aug_2025 = True
                
                period_tag = "pre-binance-blowup" if is_pre_aug_2025 else "post-blowup"
                
                matches = TRC20_PATTERN.findall(content)
                if matches:
                    print(f"Found {len(matches)} potential addresses in {filename} ({year or '?'}/{month or '?'})")
                    
                    clean_filename = filename.replace(".txt", "").replace(".json", "")
                    likely_id = None
                    for key in ledger_keys:
                        if key.lower() in clean_filename.lower():
                            likely_id = key
                            break
                    
                    for addr in set(matches):
                        address_recurrence[addr] = address_recurrence.get(addr, 0) + 1
                        if addr not in results: results[addr] = []
                        results[addr].append({
                            "file": filename,
                            "likely_identity": likely_id,
                            "period": period_tag,
                            "raw_date": f"{year}/{month}" if year else "unknown"
                        })
        except Exception as e:
            print(f"Error reading {filename}: {e}")

    # 3. Aggregated Findings
    common_addresses = sorted(address_recurrence.items(), key=lambda x: x[1], reverse=True)[:10]

    with open(OUTPUT_MAPPING, 'w', encoding='utf-8') as f:
        json.dump({
            "metrics": {
                "total_unique_addresses": len(results),
                "top_potential_senders": common_addresses
            },
            "attributions": results
        }, f, indent=2)

    print(f"Extraction complete. Found {len(results)} unique TRC20 addresses.")
    if common_addresses:
        print(f"Top Recurring Address (Potential Binance Hub): {common_addresses[0][0]} ({common_addresses[0][1]} hits)")

if __name__ == "__main__":
    refine_recovery()
