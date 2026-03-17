# strategy_ranker.py

from typing import List, Dict, Any


class StrategyRanker:
    """
    Ranks strategies based on their computed scores.
    Input: list of scored strategy dicts
    Output: sorted list (highest score first)
    """

    def __init__(self, descending: bool = True):
        self.descending = descending

    def rank(self, scored_strategies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Each scored strategy should look like:
        {
            "strategy": "Roth Conversion",
            "score": 0.67,
            "components": {...},
            "output": {...}   # optional, if you attach execution output
        }
        """

        # Defensive: ignore strategies missing a score
        valid = [s for s in scored_strategies if "score" in s]

        # Sort by score
        ranked = sorted(
            valid,
            key=lambda s: s["score"],
            reverse=self.descending
        )

        return ranked
