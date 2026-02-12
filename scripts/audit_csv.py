
import csv

def audit_csv():
    csv_file = 'data/reports/trust_health_table.csv'
    rows = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    total_effective_unpaid = sum(float(r['Effective Unpaid']) for r in rows)
    total_snowball = sum(float(r['Snowball']) for r in rows)
    total_net_harmony = sum(float(r['Net Harmony']) for r in rows)
    
    # Implied Risk Amount = Snowball - Net Harmony
    total_implied_risk_amount = sum(float(r['Snowball']) - float(r['Net Harmony']) for r in rows)

    print(f"Total Effective Unpaid (Sum of column): {total_effective_unpaid:,.2f}")
    print(f"Total Snowball: {total_snowball:,.2f}")
    print(f"Total Net Harmony: {total_net_harmony:,.2f}")
    print(f"Total Implied Risk Amount (Total Debt): {total_implied_risk_amount:,.2f}")

    # Check Trustee-001
    t1 = rows[0]
    t1_eff_unpaid = float(t1['Effective Unpaid'])
    t1_risk_pct = float(t1['Risk %'])
    t1_snowball = float(t1['Snowball'])
    t1_harmony = float(t1['Net Harmony'])
    t1_implied_risk = t1_snowball - t1_harmony
    
    print(f"\nTrustee-001 Stats:")
    print(f"Effective Unpaid: {t1_eff_unpaid:,.2f}")
    print(f"Risk % (CSV): {t1_risk_pct}%")
    print(f"Calculated Risk % (Eff/Total): {(t1_eff_unpaid / total_effective_unpaid) * 100:.4f}%")
    print(f"Implied Risk Amount: {t1_implied_risk:,.2f}")
    
    if total_implied_risk_amount > 0:
        print(f"Calculated Risk Amount (Allocated % * Total Risk): {(t1_eff_unpaid / total_effective_unpaid) * total_implied_risk_amount:,.2f}")

if __name__ == "__main__":
    audit_csv()
