from dataclasses import dataclass
from typing import Optional, Dict, Any

import pandas as pd

# Import your prediction modules
from income_volatility_predictor import IncomeVolatilityPredictor
from income_growth_predictor import IncomeGrowthPredictor
from savings_rate_predictor import SavingsRatePredictor
from deduction_probability_model import DeductionProbabilityModel
from credit_value_predictor import CreditValuePredictor
from refund_predictor import RefundPredictor
from bracket_projection import BracketProjectionModel
from tax_burden_predictor import TaxBurdenPredictor
from retirement_contribution_optimizer import RetirementContributionOptimizer
from investment_tax_impact_predictor import InvestmentTaxImpactPredictor


@dataclass
class InferenceResult:
    income_volatility: Any
    income_growth: Any
    savings_rate: Any
    deduction_probabilities: Dict[str, Any]
    credit_values: Dict[str, Any]
    bracket_projection: Any
    tax_burden: Any
    refund_estimate: Any
    retirement_contribution: Any
    investment_tax_impact: Any
    metadata: Dict[str, Any]


class InferenceEngine:
    """
    Central orchestrator for all prediction modules.
    Handles routing, dependency ordering, and unified output formatting.
    """

    def __init__(
        self,
        config: Dict[str, Any],
        ml_models: Optional[Dict[str, Any]] = None,
    ):
        self.config = config
        self.ml_models = ml_models or {}

        # Initialize predictors
        self.volatility = IncomeVolatilityPredictor(
            ml_model=self.ml_models.get("income_volatility")
        )
        self.growth = IncomeGrowthPredictor(
            ml_model=self.ml_models.get("income_growth")
        )
        self.savings = SavingsRatePredictor(
            ml_model=self.ml_models.get("savings_rate")
        )
        self.refund = RefundPredictor(
            tax_brackets=config["tax_brackets"],
            standard_deduction=config["standard_deduction"],
            ml_model=self.ml_models.get("refund"),
        )
        self.bracket = BracketProjectionModel(
            tax_brackets=config["tax_brackets"],
            standard_deduction=config["standard_deduction"],
            ml_model=self.ml_models.get("bracket_projection"),
        )
        self.tax_burden = TaxBurdenPredictor(
            tax_brackets=config["tax_brackets"],
            standard_deduction=config["standard_deduction"],
            ml_model=self.ml_models.get("tax_burden"),
        )
        self.retirement = RetirementContributionOptimizer(
            contribution_limit=config["retirement_limit"],
            marginal_tax_brackets=config["tax_brackets"],
            ml_model=self.ml_models.get("retirement"),
        )
        self.investment = InvestmentTaxImpactPredictor(
            short_term_rate=config["short_term_rate"],
            long_term_brackets=config["long_term_capital_gains_brackets"],
            qualified_dividend_rate=config["qualified_dividend_rate"],
            ordinary_income_rate=config["ordinary_income_rate"],
            crypto_rate=config["crypto_rate"],
            ml_model=self.ml_models.get("investment_tax"),
        )

    def run(
        self,
        income_history: pd.Series,
        spending_history: pd.Series,
        deduction_features: Dict[str, Dict[str, float]],
        credit_features: Dict[str, Dict[str, float]],
        investment_activity: Dict[str, float],
    ) -> InferenceResult:

        # 1. Income volatility
        vol = self.volatility.predict(income_history)

        # 2. Income growth
        growth = self.growth.predict(income_history)

        # 3. Savings rate
        savings = self.savings.predict(income_history, spending_history)

        # 4. Deduction probabilities (multiple models)
        deduction_results = {}
        for name, features in deduction_features.items():
            model = DeductionProbabilityModel(
                deduction_name=name,
                rule_weights=self.config["deduction_rules"].get(name, {}),
                ml_model=self.ml_models.get(f"deduction_{name}"),
            )
            deduction_results[name] = model.predict(features)

        # 5. Credit values (multiple models)
        credit_results = {}
        for name, features in credit_features.items():
            model = CreditValuePredictor(
                credit_name=name,
                base_amount=self.config["credit_base_amounts"][name],
                phaseout_start=self.config["credit_phaseouts"][name]["start"],
                phaseout_end=self.config["credit_phaseouts"][name]["end"],
                rule_weights=self.config["credit_rules"].get(name, {}),
                ml_model=self.ml_models.get(f"credit_{name}"),
            )
            credit_results[name] = model.predict(features)

        # Aggregate credit values
        total_credit_value = sum(v.estimated_value for v in credit_results.values())

        # 6. Bracket projection
        bracket = self.bracket.predict(
            income_history=income_history,
            projected_growth_rate=growth.projected_growth_rate,
            estimated_deductions=savings.realistic_savings_rate * income_history.sum(),
        )

        # 7. Tax burden
        tax_burden = self.tax_burden.predict(
            income_history=income_history,
            projected_growth_rate=growth.projected_growth_rate,
            estimated_deductions=savings.realistic_savings_rate * income_history.sum(),
            estimated_credits=total_credit_value,
        )

        # 8. Refund estimate
        refund = self.refund.predict(
            annual_income=income_history.sum(),
            estimated_deductions=savings.realistic_savings_rate * income_history.sum(),
            estimated_credits=total_credit_value,
            income_history=income_history,
        )

        # 9. Retirement optimization
        retirement = self.retirement.predict(
            projected_agi=tax_burden.projected_agi,
            projected_taxable_income=tax_burden.projected_taxable_income,
            projected_tax_liability=tax_burden.projected_tax_liability,
            income_history=income_history,
            volatility_penalty=vol.volatility_score,
        )

        # 10. Investment tax impact
        invest = self.investment.predict(
            short_term_gains=investment_activity.get("short_term_gains", 0.0),
            long_term_gains=investment_activity.get("long_term_gains", 0.0),
            qualified_dividends=investment_activity.get("qualified_dividends", 0.0),
            ordinary_dividends=investment_activity.get("ordinary_dividends", 0.0),
            crypto_gains=investment_activity.get("crypto_gains", 0.0),
            taxable_income=tax_burden.projected_taxable_income,
        )

        return InferenceResult(
            income_volatility=vol,
            income_growth=growth,
            savings_rate=savings,
            deduction_probabilities=deduction_results,
            credit_values=credit_results,
            bracket_projection=bracket,
            tax_burden=tax_burden,
            refund_estimate=refund,
            retirement_contribution=retirement,
            investment_tax_impact=invest,
            metadata={
                "version": self.config.get("version", "1.0"),
                "predictors_loaded": True,
            },
        )
