# constraint_checker.py

from typing import List, Dict, Any, Protocol


class Strategy(Protocol):
    """
    Strategies must implement:
    - name
    - check_constraints(user, context)
    """
    name: str

    def check_constraints(self, user: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """
        Returns a list of constraint violations.
        Empty list means the strategy is legal & feasible.
        """
        ...


class ConstraintChecker:
    """
    Evaluates whether strategies are legal and feasible.
    """

    def __init__(self, strategies: List[Strategy]):
        self.strategies = strategies

    def evaluate(self, user: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Returns a dict:
        {
            "Strategy Name": ["violation1", "violation2", ...]
        }
        Only includes strategies with violations.
        """
        violations = {}

        for strategy in self.strategies:
            try:
                issues = strategy.check_constraints(user, context)
                if issues:
                    violations[strategy.name] = issues
            except Exception:
                # If a strategy fails, treat it as invalid
                violations[strategy.name] = ["Internal error evaluating constraints"]

        return violations
