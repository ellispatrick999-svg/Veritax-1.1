from typing import List, Dict


def generate(context) -> List[Dict]:

    expenses = context.get("business_expenses", 0)

    if expenses > 0:
        return [{
            "strategy": "maximize_business_expenses",
            "estimated_savings": expenses * 0.22,
            "confidence": 0.8
        }]

    return []
