# backend/data/confidence.py
def compute_confidence(
    has_date: bool,
    has_amount: bool,
    merchant_match: bool
) -> float:
    score = 0.0
    score += 0.4 if has_amount else 0
    score += 0.3 if has_date else 0
    score += 0.3 if merchant_match else 0
    return round(score, 2)
