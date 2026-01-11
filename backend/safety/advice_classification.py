from enum import Enum

class AdviceType(Enum):
    INFORMATIONAL = "informational"
    EDUCATIONAL = "educational"
    RECOMMENDATION = "recommendation"
    HUMAN_REVIEW_REQUIRED = "human_review_required"


def classify(confidence: float, risk: float) -> AdviceType:
    if risk > 0.75:
        return AdviceType.HUMAN_REVIEW_REQUIRED
    if confidence > 0.8:
        return AdviceType.RECOMMENDATION
    return AdviceType.EDUCATIONAL
