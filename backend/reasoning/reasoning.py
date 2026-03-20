from typing import Dict, Any


class Reasoning:

    def analyze(
        self,
        financial_profile: Dict[str, Any],
        predictions: Dict[str, Any],
        tax: Dict[str, Any],
        strategies: Any,
        simulation: Dict[str, Any]
    ) -> Dict[str, Any]:

        avg_income = simulation["data"].get("average_income", 0)

        decision = "stable"

        if avg_income > 80000:
            decision = "optimize_tax_strategy"

        return {
            "source": "reasoning",
            "data": {
                "decision": decision
            },
            "confidence": 0.88
        }
