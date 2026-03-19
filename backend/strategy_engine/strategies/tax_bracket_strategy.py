from typing import List, Dict


def generate(context) -> List[Dict]:

    income = context.get("predicted_income", 0)
    threshold = context.get("next_bracket_threshold", 0)

    if threshold and (threshold - income) < 3000:
        return [{
            "strategy": "reduce_taxable_income",
            "estimated_savings": 800,
            "confidence": 0.85
        }]

    return []
