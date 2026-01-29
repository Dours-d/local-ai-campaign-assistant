from src.utils.debt_manager import DebtManager
from src.utils.trust_manager import TrustProjection
import os

def main():
    print("--- Trust Projection & Shareholder Report ---")
    
    dataset_path = "primary_campaign_dataset.csv"
    if not os.path.exists(dataset_path):
        print(f"❌ Dataset not found: {dataset_path}")
        return

    debt_manager = DebtManager(dataset_path)
    trust_engine = TrustProjection(debt_manager)
    
    total_debt = debt_manager.get_total_unsatisfied_debt()
    print(f"Total Unsatisfied Historical Debt: ${total_debt:,.2f}")
    
    print("\n--- Shareholder Breakdown (Trustee Candidates) ---")
    stats = trust_engine.get_shareholder_stats()
    
    for s in stats[:10]: # Top 10
        print(f"Shareholder: {s['shareholder'][:50]}...")
        print(f"  Debt Owed: ${s['debt_amount']:.2f}")
        print(f"  Trust Share: {s['trust_share_percent']:.2f}%")
        print("-" * 30)

    print("\n--- System Velocity & Resolution Projections ---")
    # Assume a hypothetical monthly resolution of $500 from new campaigns
    velocity = 500.0
    projection = trust_engine.project_resolution(velocity)
    
    print(f"Current Velocity: ${velocity}/month (Debt Resolution Layer)")
    print(f"Projected Time to Full Resolution: {projection['projected_months']} months")
    print(f"System Status: {projection['system_status']}")

if __name__ == "__main__":
    main()
