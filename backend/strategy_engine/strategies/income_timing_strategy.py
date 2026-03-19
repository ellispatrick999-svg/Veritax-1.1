from typing import List, Dict


def generate(context) -> List[Dict]:

    income = context.get("predicted_income", 0)
    threshold = context.get("next_bracket_threshold", 0)

    if threshold and income > threshold:
        return [{
            "strategy": "defer_income",
            "estimated_savings": 1000,
            "confidence": 0.7
        }]

    return []
