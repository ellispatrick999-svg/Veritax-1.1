from typing import Dict


class SavingsEstimator:
    """
    Estimates tax savings for strategies.
    """

    @staticmethod
    def estimate_retirement_savings(contribution: float, tax_rate: float) -> float:
        return round(contribution * tax_rate, 2)

    @staticmethod
    def estimate_deduction_savings(deduction: float, tax_rate: float) -> float:
        return round(deduction * tax_rate, 2)

    @staticmethod
    def estimate_credit_savings(credit_amount: float) -> float:
        return round(credit_amount, 2)

    @staticmethod
    def estimate_generic(strategy: Dict) -> float:
        return float(strategy.get("estimated_savings", 0))
