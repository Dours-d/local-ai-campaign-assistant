from typing import Dict, Any, Optional
import re
from .debt_manager import DebtManager
from .trust_manager import TrustProjection

class LiquidityManager:
    """
    Handles the 25% financial resolution policy and coordinates with Debt/Trust managers.
    """
    
    TOTAL_COMPROMISE = 0.25
    TRANSPARENT_RATIO = 0.15  # 10% Debt + 5% Fees
    INTERNAL_RATIO = 0.10     # 10% Management
    
    def __init__(self, dataset_path: Optional[str] = "primary_campaign_dataset.csv"):
        self.debt_manager = DebtManager(dataset_path) if dataset_path else None
        self.trust_projection = TrustProjection(self.debt_manager) if self.debt_manager else None
    
    @staticmethod
    def parse_amount(amount_str: str) -> float:
        """Extracts numerical value from currency strings like '€5,000' or '$100'"""
        if not amount_str: return 0.0
        clean = re.sub(r'[^\d.]', '', amount_str.replace(',', ''))
        return float(clean) if clean else 0.0

    def calculate_split(self, goal_amount_str: str) -> Dict[str, Any]:
        """
        Calculates the financial split and identifies which debts are resolved.
        """
        total_value = self.parse_amount(goal_amount_str)
        
        debt_resolution_val = total_value * 0.10
        transaction_fees = total_value * 0.05
        operational_cushion = total_value * 0.10
        
        # Apply to DebtManager if available
        resolutions = []
        if self.debt_manager:
            resolutions = self.debt_manager.resolve_debt(debt_resolution_val)
        
        return {
            "gross_goal": total_value,
            "net_support": total_value * (1 - self.TOTAL_COMPROMISE),
            "debt_resolution": debt_resolution_val,
            "transaction_fees": transaction_fees,
            "transparent_total": debt_resolution_val + transaction_fees,
            "operational_cushion": operational_cushion,
            "resolutions": resolutions,
            "total_resolution": total_value * self.TOTAL_COMPROMISE
        }

    def get_public_context(self, goal_amount_str: str) -> str:
        """Returns a string describing the public-facing resolution logic and trust impact"""
        split = self.calculate_split(goal_amount_str)
        debt_fmt = f"{split['debt_resolution']:.2f}".replace('.00', '')
        fees_fmt = f"{split['transaction_fees']:.2f}".replace('.00', '')
        
        note = (
            f"This campaign includes a 15% resolution policy ({self.TRANSPARENT_RATIO*100:.0f}% of total). "
            f"From the total goal, {debt_fmt} is dedicated to historical debt stabilization, "
            f"and approximately {fees_fmt} covers transactional liquidity costs."
        )
        
        if split['resolutions']:
            main_resolved = split['resolutions'][0]['shareholder']
            note += f" This contribution directly supports the resolution of debt for: {main_resolved}."
            
        return note
