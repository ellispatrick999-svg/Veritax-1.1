# strategy_filter.py

from typing import List, Protocol, Dict, Any


class Strategy(Protocol):
    """
    Every strategy must implement `is_applicable`.
    This keeps the filter generic and future-proof.
    """
    name: str

    def is_applicable(self, user: Dict[str, Any], context: Dict[str, Any]) -> bool:
        ...


class StrategyFilter:
    """
    Filters out strategies that do not apply to the user.
    """

    def __init__(self, strategies: List[Strategy]):
        self.strategies = strategies

    def filter(self, user: Dict[str, Any], context: Dict[str, Any]) -> List[Strategy]:
        """
        Returns only strategies whose applicability rules return True.
        """
        applicable = []

        for strategy in self.strategies:
            try:
                if strategy.is_applicable(user, context):
                    applicable.append(strategy)
            except Exception as e:
                # You can log this if you have a logging layer
                # but we never want a single strategy to break the pipeline
                continue

        return applicable
