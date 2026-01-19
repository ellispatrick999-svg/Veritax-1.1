from typing import List, Dict, Any

from constants import MAX_REASONING_ITEMS
from exceptions import ExplainabilityError


class ExplainabilityEngine:
    def build(
        self,
        recommendation_title: str,
        reasoning: List[str],
        assumptions: List[str],
        tax_codes: List[str]
    ) -> Dict[str, Any]:
        if not reasoning:
            raise ExplainabilityError("No reasoning provided")

        return {
            "recommendation": recommendation_title,
            "why_this_applies": reasoning[:MAX_REASONING_ITEMS],
            "assumptions_used": assumptions,
            "tax_code_references": tax_codes,
            "disclaimer": self._disclaimer()
        }

    def _disclaimer(self) -> str:
        return (
            "This analysis is based on provided information and current tax rules. "
            "It does not constitute legal or tax advice."
        )
