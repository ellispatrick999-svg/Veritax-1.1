class ConfidenceThresholds:
    RECOMMEND = 0.80
    EXPLAIN_ONLY = 0.60

    @classmethod
    def evaluate(cls, confidence: float) -> str:
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("Confidence must be between 0 and 1.")

        if confidence >= cls.RECOMMEND:
            return "recommend"
        elif confidence >= cls.EXPLAIN_ONLY:
            return "explain"
        else:
            return "escalate"
