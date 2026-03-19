from typing import Dict


class StrategyExplainer:
    """
    Generates human-readable explanations.
    """

    def explain(self, strategy: Dict) -> str:

        name = strategy.get("strategy")
        savings = strategy.get("estimated_savings", 0)

        if name == "increase_401k":
            return f"Contributing more to your 401k could save approximately ${savings} in taxes."

        if name == "itemize_deductions":
            return f"Itemizing deductions may reduce your taxes by about ${savings}."

        return f"This strategy could save you approximately ${savings}."
