import pandas as pd
from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class InvestmentTaxImpact:
    effective_tax_rate: float
    total_tax_due: float
    short_term_tax: float
    long_term_tax: float
    dividend_tax: float
    crypto_tax: float
    ml_adjustment: float
    metadata: Dict[str, Any]


class InvestmentTaxImpactPredictor:
    """
    Predicts the effective tax impact of capital gains, dividends, and crypto trades.
    Combines rule-based tax calculations with optional ML-based adjustments.
    """

    def __init__(
        self,
        short_term_rate: float,
        long_term_brackets: Dict[float, float],
        qualified_dividend_rate: float,
        ordinary_income_rate: float,
        crypto_rate: float,
        ml_model: Optional[Any] = None,
    ):
        self.short_term_rate = short_term_rate
        self.long_term_brackets = long_term_brackets
        self.qualified_dividend_rate = qualified_dividend_rate
        self.ordinary_income_rate = ordinary_income_rate
        self.crypto_rate = crypto_rate
        self.ml_model = ml_model

    def _long_term_rate(self, taxable_income: float) -> float:
        last_limit = 0.0
        for bracket_limit, rate in sorted(self.long_term_brackets.items()):
            if taxable_income <= bracket_limit:
                return float(rate)
            last_limit = bracket_limit
        return float(list(self.long_term_brackets.values())[-1])

    def _compute_long_term_tax(self, long_term_gains: float, taxable_income: float) -> float:
        rate = self._long_term_rate(taxable_income)
        return long_term_gains * rate

    def _compute_short_term_tax(self, short_term_gains: float) -> float:
        return short_term_gains * self.short_term_rate

    def _compute_dividend_tax(self, qualified: float, ordinary: float) -> float:
        q_tax = qualified * self.qualified_dividend_rate
        o_tax = ordinary * self.ordinary_income_rate
        return q_tax + o_tax

    def _compute_crypto_tax(self, crypto_gains: float) -> float:
        return crypto_gains * self.crypto_rate

    def _ml_adjustment(self, features: Dict[str, float]) -> float:
        if self.ml_model is None:
            return 0.0
        df = pd.DataFrame([features])
        return float(self.ml_model.predict(df)[0])

    def predict(
        self,
        short_term_gains: float,
        long_term_gains: float,
        qualified_dividends: float,
        ordinary_dividends: float,
        crypto_gains: float,
        taxable_income: float,
    ) -> InvestmentTaxImpact:

        st_tax = self._compute_short_term_tax(short_term_gains)
        lt_tax = self._compute_long_term_tax(long_term_gains, taxable_income)
        div_tax = self._compute_dividend_tax(qualified_dividends, ordinary_dividends)
        crypto_tax = self._compute_crypto_tax(crypto_gains)

        base_tax = st_tax + lt_tax + div_tax + crypto_tax
        total_investment_income = (
            short_term_gains
            + long_term_gains
            + qualified_dividends
            + ordinary_dividends
            + crypto_gains
        )

        effective_rate = (
            base_tax / max(total_investment_income, 1e-6)
            if total_investment_income > 0
            else 0.0
        )

        ml_adj = self._ml_adjustment(
            {
                "short_term": short_term_gains,
                "long_term": long_term_gains,
                "qualified_dividends": qualified_dividends,
                "ordinary_dividends": ordinary_dividends,
                "crypto_gains": crypto_gains,
                "taxable_income": taxable_income,
                "base_tax": base_tax,
            }
        )

        final_effective_rate = max(0.0, effective_rate + ml_adj)
        final_tax = max(0.0, base_tax + ml_adj)

        return InvestmentTaxImpact(
            effective_tax_rate=float(final_effective_rate),
            total_tax_due=float(final_tax),
            short_term_tax=float(st_tax),
            long_term_tax=float(lt_tax),
            dividend_tax=float(div_tax),
            crypto_tax=float(crypto_tax),
            ml_adjustment=float(ml_adj),
            metadata={
                "long_term_brackets": self.long_term_brackets,
                "short_term_rate": self.short_term_rate,
                "qualified_dividend_rate": self.qualified_dividend_rate,
                "ordinary_income_rate": self.ordinary_income_rate,
                "crypto_rate": self.crypto_rate,
            },
        )
