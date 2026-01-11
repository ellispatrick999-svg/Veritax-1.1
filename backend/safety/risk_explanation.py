def generate_risk_explanation(reasons: list[str]) -> str:
    if not reasons:
        return "No significant risks detected."

    explanation = "Potential risk factors identified:\n"
    for idx, reason in enumerate(reasons, 1):
        explanation += f"{idx}. {reason}\n"

    return explanation
