import pandas as pd
from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class RefundPrediction:
    estimated_refund: float
    estimated_tax_liability: float
    estimated_withholding: float
    estimated_deductions: float
    estimated_credits: float
    ml_adjustment: float
    metadata: Dict[str, Any]


class RefundPredictor:
    """
    Estimates a user's expected tax refund (or amount owed) before filing.
    Combines rule-based tax liability estimation with withholding, deductions,
    credits, and optional ML-based adjustments.
    """

    def __init__(
        self,
        tax_brackets: Dict[str, float],
        standard_deduction: float,
        ml_model: Optional[Any] = None,
    ):
        self.tax_brackets = tax_brackets
        self.standard_deduction = standard_deduction
        self.ml_model = ml_model

    def _estimate_tax_liability(self, taxable_income: float) -> float:
        remaining = taxable_income
        tax = 0.0
        last_limit = 0.0

        for bracket_limit, rate in sorted(self.tax_brackets.items()):
            if remaining <= 0:
                break
            bracket_income = min(remaining, bracket_limit - last_limit)
            tax += bracket_income * rate
            remaining -= bracket_income
            last_limit = bracket_limit

        return max(0.0, tax)

    def _estimate_withholding(self, income_series: pd.Series) -> float:
        return float(income_series.sum() * 0.18)

    def _ml_adjustment(self, features: Dict[str, float]) -> float:
        if self.ml_model is None:
            return 0.0
        df = pd.DataFrame([features])
        return float(self.ml_model.predict(df)[0])

    def predict(
        self,
        annual_income: float,
        estimated_deductions: float,
        estimated_credits: float,
        income_history: Optional[pd.Series] = None,
    ) -> RefundPrediction:

        taxable_income = max(
            0.0,
            annual_income - max(estimated_deductions, self.standard_deduction),
        )

        tax_liability = self._estimate_tax_liability(taxable_income)

        withholding = (
            self._estimate_withholding(income_history)
            if income_history is not None
            else annual_income * 0.18
        )

        base_refund = withholding - tax_liability + estimated_credits

        ml_adj = self._ml_adjustment(
            {
                "annual_income": annual_income,
                "taxable_income": taxable_income,
                "estimated_deductions": estimated_deductions,
                "estimated_credits": estimated_credits,
                "withholding": withholding,
            }
        )

        estimated_refund = base_refund + ml_adj

        return RefundPrediction(
            estimated_refund=float(estimated_refund),
            estimated_tax_liability=float(tax_liability),
            estimated_withholding=float(withholding),
            estimated_deductions=float(estimated_deductions),
            estimated_credits=float(estimated_credits),
            ml_adjustment=float(ml_adj),
            metadata={
                "tax_brackets": self.tax_brackets,
                "standard_deduction": self.standard_deduction,
                "taxable_income": taxable_income,
            },
        )
