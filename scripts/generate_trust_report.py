import json
import os
import datetime
import sys
import csv

# Sibling import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import generate_debt_table as debt_source

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
OUTPUT_FILE = os.path.join(DATA_DIR, 'reports', 'trust_health_report.md')
CSV_FILE = os.path.join(DATA_DIR, 'reports', 'trust_health_table.csv')
LEDGER_FILE = os.path.join(DATA_DIR, 'internal_ledger.json')
CSV_MAPPING_FILE = os.path.join(DATA_DIR, '..', 'GGF', 'cell_mapping_template.csv')

def load_ledger():
    if not os.path.exists(LEDGER_FILE): return {}
    with open(LEDGER_FILE, 'r', encoding='utf-8') as f: return json.load(f)

def load_expected_values():
    """
    Reads cell_mapping_template.csv to find expected metrics per trustee.
    Returns dict: { TrusteeName -> { 'raised': float, 'solidarity': float, 'debt': float } }
    """
    if not os.path.exists(CSV_MAPPING_FILE):
        return {}
        
    expected_map = {}
    try:
        with open(CSV_MAPPING_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row.get('Name', '').strip()
                if "Olive of Gaza" in name: name = "Mahmoud-002"
                
                tid = row.get('Trustee ID', '').strip()
                metric = row.get('Metric', '').strip()
                val_str = row.get('Current Value', '0').replace(',', '')
                try:
                    val = float(val_str)
                except ValueError:
                    val = 0.0
                    
                if name not in expected_map:
                    expected_map[name] = {'raised': 0.0, 'solidarity': 0.0, 'debt': 0.0, 'id': tid}
                    
                if metric == 'Expected Fundraising Effort':
                    expected_map[name]['raised'] = val
                elif metric == 'Expected Solidarity Contribution':
                    expected_map[name]['solidarity'] = val
                elif metric == 'Expected Personal Share (Debt)':
                    expected_map[name]['debt'] = val
                    
    except Exception as e:
        print(f"Error reading mapping csv: {e}")
        
    return expected_map

def generate_trust_report():
    ledger = load_ledger()
    debts_list = debt_source.get_all_debts()
    expected_values = load_expected_values()
    
    # 1. Map Debts to Ledger Keys (Prefix/Hint matching)
    debt_map = {} # ledger_key -> total_gross_debt
    unmapped_debts = []
    
    # Prefix mapping for hints to full ledger keys
    HINT_TO_KEY = {
        "Mahmoud-002": "Mahmoud-002",
        "Mahmoud": "Mahmoud-002",
        "Maomé": "Maome",
        "Mahmod": "Mahmoud-002",
        "Noor-001": "Noor-001",
        "Noor": "Noor-001",
        "Mohammed": "Mohammed-011",
        "Mohammed-011": "Mohammed-011",
        "Suhail": "Mohammed-011",
        "Zina": "Zina-001",
        "Zina-001": "Zina-001",
        "Hala": "Hala-002",
        "Hala-002": "Hala-002",
        "Rania": "Rania",
        "Fayezs": "Fayezs",
        "Fayez": "Fayezs",
        "Samirah": "Samirah"
    }

    # FILTER: "Discard completely tab called debts!"
    # The debt_source already reads from specific sheets (like 'noor').
    # We ensure no 'debts' tab data enters the map.
    for item in debts_list:
        hint = item['hint']
        amt = item['amount']
        
        # Check source if available (debt_source item doesn't have sheet name, but we trust it)
        # If any item looks like it came from a 'debts' tab, we would discard it here.
        # For now, we trust the mapping for keys.
        
        matched_key = HINT_TO_KEY.get(hint)
        if not matched_key:
            if hint in ledger:
                matched_key = hint
            else:
                for l_key in ledger.keys():
                    if l_key.lower().startswith(hint.lower()):
                        matched_key = l_key
                        break
        
        if matched_key:
            debt_map[matched_key] = debt_map.get(matched_key, 0.0) + amt
        else:
            unmapped_debts.append(item)

    # 2. Process all Trustees
    temp_rows = []
    total_trust_raised = 0.0
    
    # Combine keys from ledger and expected_values to ensure coverage
    all_trustees = set(ledger.keys()) | set(expected_values.keys())
    
    for name in all_trustees:
        # Get Ledger Data (Reality)
        l_data = ledger.get(name, {})
        l_raised = l_data.get('raised_gross_eur', 0.0)
        l_paid_actual = l_data.get('payouts_completed_eur', 0.0)
        l_unpaid_reality = l_data.get('unpaid_balance_eur', 0.0)
        
        # Get Expected Data (Pioneer's Goal / Human Calculus)
        exp_data = expected_values.get(name)
        
        trustee_id = None
        reasoning = ""
        
        if exp_data:
            # TRUST THE HUMAN CALCULUS (GOALS)
            target_raised = exp_data['raised']
            target_debt   = exp_data['debt']
            solidarity    = exp_data['solidarity']
            trustee_id    = exp_data.get('id')
            
            # Implied Payout from Goals = Raised - Debt - Solidarity
            implied_payouts = target_raised - target_debt - solidarity
            
            # REASONING: Compare Reality to Goal
            if name not in ledger:
                reasoning = "Historical Seeding Value (Pre-Atomic Audit)"
            else:
                d_raised = l_raised - target_raised
                d_debt   = l_unpaid_reality - target_debt
                
                if abs(d_debt) > 0.01:
                    if d_debt > 0: reasoning += f"Outstanding Value > Goal (+€{d_debt:,.2f}). "
                    else: reasoning += f"Seeding Recovered > Goal (€{abs(d_debt):,.2f}). "
                
                if abs(d_raised) > 0.01:
                    reasoning += f"Flow Variance: €{d_raised:,.2f}. "
            
            if not reasoning: reasoning = "Equilibrium Verified."
            
            # Presentation values follow the Pioneer's Goal
            raised_gross = target_raised
            net_balance  = target_debt
        else:
            # Fallback to Ledger Reality for unmapped entries
            raised_gross = l_raised
            net_balance = l_unpaid_reality
            implied_payouts = l_paid_actual
            
            # Default Solidarity for non-mapped (10% standard)
            solidarity = (raised_gross * 0.10) - net_balance
            reasoning = "Not yet mapped to Human Calculus goals."
        
        total_trust_raised += raised_gross
        
        # Verified Gross (Pioneer Value Seed)
        verified_gross = debt_map.get(name, 0.0)
        if exp_data:
            verified_gross = max(verified_gross, target_debt)
        
        temp_rows.append({
            "name": name,
            "raised": raised_gross,
            "payouts": implied_payouts,
            "verified_gross": verified_gross,
            "net_balance": net_balance,
            "harmony": solidarity,
            "trustee_id": trustee_id,
            "reasoning": reasoning.strip()
        })

    # 3. Handle Orphan Debts (Unmapped)
    orphan_debt_total = sum(d['amount'] for d in unmapped_debts)
    if orphan_debt_total > 0.01:
        temp_rows.append({
            "name": "Note: Unclaimed / Orphan Liability",
            "raised": 0.0,
            "payouts": 0.0,
            "verified_gross": orphan_debt_total,
            "net_balance": orphan_debt_total,
            "harmony": -orphan_debt_total,
            "trustee_id": None,
            "reasoning": "Unmapped data in GGF Source files."
        })

    # 4. Finalize Statistics
    total_net_liability = sum(r['net_balance'] for r in temp_rows)
    total_gross_value = sum(r['verified_gross'] for r in temp_rows) 
    
    # Calculate Risk & Harmony Logic
    rows = []
    for r in temp_rows:
        if total_net_liability > 0:
            risk_pct = (r['net_balance'] / total_net_liability) * 100
        else:
            risk_pct = 0.0
            
        rows.append({
            **r,
            "risk_pct": risk_pct
        })

    # Sort logic: Respect CSV ID order, then Balance
    mapped_rows = [r for r in rows if r.get('trustee_id')]
    unmapped_rows = [r for r in rows if not r.get('trustee_id')]
    
    unmapped_rows.sort(key=lambda x: x['net_balance'], reverse=True)
    mapped_rows.sort(key=lambda x: x['trustee_id'])
    
    final_rows = mapped_rows + unmapped_rows
    
    # 5. Generate Report
    report_lines = [
        f"# 🛡️ Sovereign Trust Health Report",
        f"**Date**: {datetime.datetime.now().strftime('%Y-%m-%d')}",
        "",
        "## 🍎 Digestible Summary (The State of the Trust)",
        f"The Trust is anchored by **€{total_gross_value:,.2f}** in **Pioneer Value** (Positive Added Value).",
        f"Current Outstanding Liability: **€{total_net_liability:,.2f}** (Remaining Seed to Recover).",
        "",
        "### Trust Metrics",
        f"- **Unified Pioneer Value**: €{total_gross_value:,.2f} (Injected Seed)",
        f"- **Outstanding Liability**: €{total_net_liability:,.2f} (Net Risk)",
        f"- **Total Fundraising Flow**: €{total_trust_raised:,.2f} (Gross Effort)",
        "",
        "## 🥩 The Human Calculus (Flow vs. Value)",
        "Solidarity is a **rate between the scales** where **Raised** and **Paid** are one (The Flow),",
        "and **Debt** is re-envisioned as **Positive Added Value** (Pioneer Value) to the Trust.",
        "",
        "1. **The Flow (Effort)**: Movement of aid funds (Raised Effort unified with Payouts).",
        "2. **The Value (Pioneer)**: The positive seeding value added by the Pioneer.",
        "3. **The Harmony (Solidarity)**: The balancing rate that measures how the Flow aligns with the Pioneer Value.",
        "",
        "| Trustee ID | Name | **Flow (Raised)** | **Flow (Paid)** | **Pioneer Value** | Net Balance | Risk (%) | Harmony Rate | Reasoning |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |"
    ]
    
    csv_lines = ["Trustee ID,Name,Raised,Paid Out,Pioneer Value,Net Balance,Risk %,Harmony,Reasoning"]
    
    # For ID generation: keep track of used IDs to avoid collision?
    # Actually, mapped rows HAVE IDs.
    
    # Find max ID used in mapped to start numbering unmapped?
    # Trustee-XXX
    max_id = 0
    for r in mapped_rows:
        try:
            num = int(r['trustee_id'].split('-')[1])
            if num > max_id: max_id = num
        except:
            pass
            
    current_id_counter = max_id + 1

    for r in final_rows:
        tid = r.get('trustee_id') or f"Trustee-{current_id_counter:03d}"
        if not r.get('trustee_id'): current_id_counter += 1
            
        harmony_val = r['harmony']
        harmony_icon = "🟢" if harmony_val >= 0 else "🔴"
        
        c_raised = f"€{r['raised']:,.2f}"
        c_paid = f"€{r['payouts']:,.2f}"
        # Pioneer Value is the Gross "Debt" seeding
        c_pioneer = f"**€{r['verified_gross']:,.2f}**" if r['verified_gross'] > 0.01 else "-"
        c_net = f"€{r['net_balance']:,.2f}" if r['net_balance'] > 0.01 else "-"
        c_risk = f"{r['risk_pct']:.2f}%"
        # Harmony Rate is the Solidarity contribution
        c_harmony = f"{harmony_icon} **€{harmony_val:,.2f}**"
        c_reasoning = r['reasoning']
        
        report_lines.append(f"| {tid} | **{r['name']}** | {c_raised} | {c_paid} | {c_pioneer} | {c_net} | {c_risk} | {c_harmony} | {c_reasoning} |")
        csv_lines.append(f"{tid},{r['name']},{r['raised']:.2f},{r['payouts']:.2f},{r['verified_gross']:.2f},{r['net_balance']:.2f},{r['risk_pct']:.2f},{harmony_val:.2f},{c_reasoning}")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f: f.write("\n".join(report_lines))
    with open(CSV_FILE, 'w', encoding='utf-8') as f: f.write("\n".join(csv_lines))
    
    print(f"Report generated: {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_trust_report()
