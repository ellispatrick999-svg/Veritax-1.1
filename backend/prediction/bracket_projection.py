import pandas as pd
from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class BracketProjection:
    projected_bracket: str
    projected_taxable_income: float
    projected_agi: float
    estimated_deductions: float
    ml_adjustment: float
    metadata: Dict[str, Any]


class BracketProjectionModel:
    """
    Predicts the tax bracket a user will fall into based on projected AGI,
    deductions, credits, and optional ML-based adjustments.
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

    def _project_agi(self, income_history: pd.Series, growth_rate: float) -> float:
        current_annual = float(income_history.sum())
        return current_annual * (1 + growth_rate)

    def _compute_taxable_income(self, agi: float, deductions: float) -> float:
        deduction_used = max(deductions, self.standard_deduction)
        return max(0.0, agi - deduction_used)

    def _determine_bracket(self, taxable_income: float) -> str:
        last_limit = 0.0
        for bracket_limit, rate in sorted(self.tax_brackets.items()):
            if taxable_income <= bracket_limit:
                return f"{int(rate * 100)}%"
            last_limit = bracket_limit
        return f"{int(list(self.tax_brackets.values())[-1] * 100)}%"

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
    ) -> BracketProjection:

        agi = self._project_agi(income_history, projected_growth_rate)
        taxable_income = self._compute_taxable_income(agi, estimated_deductions)
        bracket = self._determine_bracket(taxable_income)

        ml_adj = self._ml_adjustment(
            {
                "agi": agi,
                "taxable_income": taxable_income,
                "deductions": estimated_deductions,
                "growth_rate": projected_growth_rate,
            }
        )

        return BracketProjection(
            projected_bracket=bracket,
            projected_taxable_income=float(taxable_income),
            projected_agi=float(agi),
            estimated_deductions=float(estimated_deductions),
            ml_adjustment=float(ml_adj),
            metadata={
                "tax_brackets": self.tax_brackets,
                "standard_deduction": self.standard_deduction,
                "growth_rate": projected_growth_rate,
                "months_of_history": len(income_history),
            },
        )
