# strategy_validator.py

from typing import List, Dict, Any, Protocol


class Strategy(Protocol):
    """
    Strategies must implement:
    - name
    - validate_assumptions(user, context)
    """
    name: str

    def validate_assumptions(self, user: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """
        Returns a list of failed assumptions.
        Empty list means the strategy's assumptions hold true.
        """
        ...


class StrategyValidator:
    """
    Validates strategy assumptions before they are applied.
    """

    def __init__(self, strategies: List[Strategy]):
        self.strategies = strategies

    def validate(self, user: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Returns:
        {
            "Strategy Name": ["failed assumption 1", "failed assumption 2"]
        }
        Only includes strategies with failed assumptions.
        """
        failed = {}

        for strategy in self.strategies:
            try:
                issues = strategy.validate_assumptions(user, context)
                if issues:
                    failed[strategy.name] = issues
            except Exception:
                failed[strategy.name] = ["Internal error validating assumptions"]

        return failed
