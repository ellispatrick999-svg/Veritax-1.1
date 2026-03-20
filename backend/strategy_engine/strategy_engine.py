from dataclasses import dataclass
from typing import Dict, Any, List

from inference_engine import InferenceResult


@dataclass
class Strategy:
    name: str
    description: str
    priority: int
    expected_impact: float
    metadata: Dict[str, Any]


@dataclass
class StrategyEngineResult:
    strategies: List[Strategy]
    metadata: Dict[str, Any]


class StrategyEngine:
    """
    Converts prediction outputs into actionable tax and financial strategies.
    This layer interprets the inference layer and produces prioritized guidance.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    # -----------------------------
    # Strategy Generators
    # -----------------------------

    def _income_volatility_strategies(self, inference: InferenceResult) -> List[Strategy]:
        vol = inference.income_volatility.volatility_score
        strategies = []

        if vol > 0.7:
            strategies.append(
                Strategy(
                    name="Increase Emergency Savings",
                    description="Your income is highly volatile. Increasing your emergency fund can reduce risk.",
                    priority=1,
                    expected_impact=0.8,
                    metadata={"volatility_score": vol},
                )
            )
        elif vol > 0.4:
            strategies.append(
                Strategy(
                    name="Stabilize Cash Flow",
                    description="Moderate income volatility detected. Consider smoothing expenses or adjusting withholding.",
                    priority=3,
                    expected_impact=0.5,
                    metadata={"volatility_score": vol},
                )
            )

        return strategies

    def _retirement_strategies(self, inference: InferenceResult) -> List[Strategy]:
        rec = inference.retirement_contribution
        strategies = []

        if rec.optimal_contribution > 0:
            strategies.append(
                Strategy(
                    name="Optimize Retirement Contributions",
                    description=f"Contribute up to ${rec.optimal_contribution:.2f} to maximize tax savings.",
                    priority=2,
                    expected_impact=rec.expected_tax_savings,
                    metadata={
                        "marginal_rate": rec.marginal_tax_rate,
                        "affordability": rec.affordability_score,
                    },
                )
            )

        return strategies

    def _deduction_strategies(self, inference: InferenceResult) -> List[Strategy]:
        strategies = []

        for name, result in inference.deduction_probabilities.items():
            if result.probability > 0.6:
                strategies.append(
                    Strategy(
                        name=f"Claim {name} Deduction",
                        description=f"You have a high probability of qualifying for the {name} deduction.",
                        priority=3,
                        expected_impact=result.rule_based_score,
                        metadata={"probability": result.probability},
                    )
                )

        return strategies

    def _credit_strategies(self, inference: InferenceResult) -> List[Strategy]:
        strategies = []

        for name, result in inference.credit_values.items():
            if result.estimated_value > 0:
                strategies.append(
                    Strategy(
                        name=f"Maximize {name} Credit",
                        description=f"Estimated credit value: ${result.estimated_value:.2f}. Ensure all qualifying actions are taken.",
                        priority=2,
                        expected_impact=result.estimated_value,
                        metadata={"eligibility_probability": result.eligibility_probability},
                    )
                )

        return strategies

    def _refund_strategies(self, inference: InferenceResult) -> List[Strategy]:
        refund = inference.refund_estimate.estimated_refund
        strategies = []

        if refund < 0:
            strategies.append(
                Strategy(
                    name="Adjust Withholding",
                    description="You are projected to owe taxes. Adjust your withholding to avoid penalties.",
                    priority=1,
                    expected_impact=abs(refund),
                    metadata={"refund_projection": refund},
                )
            )
        elif refund > 2000:
            strategies.append(
                Strategy(
                    name="Reduce Over-Withholding",
                    description="You are projected to receive a large refund. Consider reducing withholding to improve cash flow.",
                    priority=4,
                    expected_impact=refund,
                    metadata={"refund_projection": refund},
                )
            )

        return strategies

    def _investment_strategies(self, inference: InferenceResult) -> List[Strategy]:
        invest = inference.investment_tax_impact
        strategies = []

        if invest.short_term_tax > invest.long_term_tax:
            strategies.append(
                Strategy(
                    name="Shift to Long-Term Holdings",
                    description="Short-term gains are taxed more heavily. Consider holding assets longer to reduce tax impact.",
                    priority=3,
                    expected_impact=invest.short_term_tax - invest.long_term_tax,
                    metadata={"effective_tax_rate": invest.effective_tax_rate},
                )
            )

        if invest.crypto_tax > 0:
            strategies.append(
                Strategy(
                    name="Plan for Crypto Tax Events",
                    description="Crypto gains detected. Ensure proper tracking and consider tax-loss harvesting.",
                    priority=4,
                    expected_impact=invest.crypto_tax,
                    metadata={"crypto_tax": invest.crypto_tax},
                )
            )

        return strategies

    # -----------------------------
    # Main Strategy Engine
    # -----------------------------

    def generate_strategies(self, inference: InferenceResult) -> StrategyEngineResult:
        strategies = []

        strategies += self._income_volatility_strategies(inference)
        strategies += self._retirement_strategies(inference)
        strategies += self._deduction_strategies(inference)
        strategies += self._credit_strategies(inference)
        strategies += self._refund_strategies(inference)
        strategies += self._investment_strategies(inference)

        # Sort by priority (1 = highest)
        strategies.sort(key=lambda s: s.priority)

        return StrategyEngineResult(
            strategies=strategies,
            metadata={"strategy_count": len(strategies)},
        )
