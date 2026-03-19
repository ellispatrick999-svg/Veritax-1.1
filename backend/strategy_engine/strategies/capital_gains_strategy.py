from typing import List, Dict


def generate(context) -> List[Dict]:

    gains = context.get("capital_gains", 0)

    if gains > 0:
        return [{
            "strategy": "harvest_losses",
            "estimated_savings": gains * 0.15,
            "confidence": 0.75
        }]

    return []
