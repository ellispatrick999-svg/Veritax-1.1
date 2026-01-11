def requires_human_review(risk: float, confidence: float) -> bool:
    return risk > 0.75 or confidence < 0.6
