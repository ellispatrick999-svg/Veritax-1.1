import pandas as pd
from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class TaxBurdenPrediction:
    effective_tax_rate: float
    projected_tax_liability: float
    projected_agi: float
    projected_taxable_income: float
    estimated_deductions: float
    estimated_credits: float
    ml_adjustment: float
    metadata: Dict[str, Any]


class TaxBurdenPredictor:
    """
    Predicts a user's effective tax rate by estimating AGI, taxable income,
    tax liability, deductions, credits, and optional ML-based adjustments.
    """

    def __init__(
        self,
        tax_brackets: Dict[float, float],
        standard_deduction: float,
        ml_model: Optional[Any] = None,
    ):
        self.tax_brackets = tax_brackets
        self.standard_deduction = standard_deduction
        self.ml_model = ml_model

    def _project_agi(self, income_history: pd.Series, growth_rate: float) -> float:
        current_annual = float(income_history.sum())
        return current_annual * (1 + growth_rate)

    def _compute_taxable_income(self, agi: float, deductions: float) -> float:
        deduction_used = max(deductions, self.standard_deduction)
        return max(0.0, agi - deduction_used)

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

    def _ml_adjustment(self, features: Dict[str, float]) -> float:
        if self.ml_model is None:
            return 0.0
        df = pd.DataFrame([features])
        return float(self.ml_model.predict(df)[0])

    def predict(
        self,
        income_history: pd.Series,
        projected_growth_rate: float,
        estimated_deductions: float,
        estimated_credits: float,
    ) -> TaxBurdenPrediction:

        agi = self._project_agi(income_history, projected_growth_rate)
        taxable_income = self._compute_taxable_income(agi, estimated_deductions)
        tax_liability = self._estimate_tax_liability(taxable_income)
        effective_rate = max(0.0, (tax_liability - estimated_credits) / max(agi, 1e-6))

        ml_adj = self._ml_adjustment(
            {
                "agi": agi,
                "taxable_income": taxable_income,
                "deductions": estimated_deductions,
                "credits": estimated_credits,
                "growth_rate": projected_growth_rate,
                "tax_liability": tax_liability,
            }
        )

        final_rate = max(0.0, effective_rate + ml_adj)

        return TaxBurdenPrediction(
            effective_tax_rate=float(final_rate),
            projected_tax_liability=float(tax_liability),
            projected_agi=float(agi),
            projected_taxable_income=float(taxable_income),
            estimated_deductions=float(estimated_deductions),
            estimated_credits=float(estimated_credits),
            ml_adjustment=float(ml_adj),
            metadata={
                "tax_brackets": self.tax_brackets,
                "standard_deduction": self.standard_deduction,
                "growth_rate": projected_growth_rate,
                "months_of_history": len(income_history),
            },
        )
