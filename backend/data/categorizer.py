"""
categorizer.py

CPA-grade expense categorization engine.
Classifies receipts into IRS-relevant expense categories
using deterministic, explainable rules.

This module must remain rules-based (no ML) to preserve
auditability and reproducibility.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional


# ----------------------------------
# Models
# ----------------------------------

@dataclass(frozen=True)
class CategorizationResult:
    category: str
    confidence: Decimal
    rationale: List[str]


# ----------------------------------
# Categories (IRS-Aligned)
# ----------------------------------

CATEGORY_MEALS = "MEALS"
CATEGORY_TRAVEL = "TRAVEL"
CATEGORY_LODGING = "LODGING"
CATEGORY_OFFICE_SUPPLIES = "OFFICE_SUPPLIES"
CATEGORY_VEHICLE = "VEHICLE"
CATEGORY_SOFTWARE = "SOFTWARE"
CATEGORY_PROFESSIONAL_SERVICES = "PROFESSIONAL_SERVICES"
CATEGORY_UTILITIES = "UTILITIES"
CATEGORY_RENT = "RENT"
CATEGORY_UNCATEGORIZED = "UNCATEGORIZED"


# ----------------------------------
# Keyword Maps
# ----------------------------------

MEALS_KEYWORDS = {
    "restaurant",
    "cafe",
    "coffee",
    "grill",
    "bar",
    "bistro",
    "diner",
    "pizza",
    "burger",
}

TRAVEL_KEYWORDS = {
    "airlines",
    "airways",
    "flight",
    "uber",
    "lyft",
    "taxi",
    "train",
    "bus",
}

LODGING_KEYWORDS = {
    "hotel",
    "inn",
    "resort",
    "motel",
    "airbnb",
}

OFFICE_SUPPLIES_KEYWORDS = {
    "staples",
    "office depot",
    "office max",
    "paper",
    "printer",
    "ink",
}

SOFTWARE_KEYWORDS = {
    "software",
    "subscription",
    "license",
    "saas",
    "cloud",
}

PROFESSIONAL_SERVICES_KEYWORDS = {
    "consulting",
    "legal",
    "attorney",
    "accounting",
    "cpa",
}

UTILITIES_KEYWORDS = {
    "electric",
    "gas",
    "water",
    "internet",
    "utility",
}

VEHICLE_KEYWORDS = {
    "gasoline",
    "fuel",
    "oil",
    "repair",
    "auto",
    "vehicle",
}


# ----------------------------------
# Public API
# ----------------------------------

def categorize_expense(receipt) -> CategorizationResult:
    """
    Categorize a receipt using deterministic keyword rules.

    Expected receipt attributes:
    - vendor: Optional[str]
    - raw_text: str
    - total: Decimal | float

    Returns:
        CategorizationResult
    """
    text = _normalize_text(
        receipt.vendor,
        getattr(receipt, "raw_text", "")
    )

    rules = [
        (_match_keywords(text, MEALS_KEYWORDS), CATEGORY_MEALS),
        (_match_keywords(text, TRAVEL_KEYWORDS), CATEGORY_TRAVEL),
        (_match_keywords(text, LODGING_KEYWORDS), CATEGORY_LODGING),
        (_match_keywords(text, OFFICE_SUPPLIES_KEYWORDS), CATEGORY_OFFICE_SUPPLIES),
        (_match_keywords(text, SOFTWARE_KEYWORDS), CATEGORY_SOFTWARE),
        (_match_keywords(text, PROFESSIONAL_SERVICES_KEYWORDS), CATEGORY_PROFESSIONAL_SERVICES),
        (_match_keywords(text, UTILITIES_KEYWORDS), CATEGORY_UTILITIES),
        (_match_keywords(text, VEHICLE_KEYWORDS), CATEGORY_VEHICLE),
    ]

    matched = [(score, category) for score, category in rules if score > 0]

    if not matched:
        return CategorizationResult(
            category=CATEGORY_UNCATEGORIZED,
            confidence=Decimal("0.00"),
            rationale=["No category rules matched."]
        )

    matched.sort(reverse=True, key=lambda x: x[0])
    score, category = matched[0]

    confidence = _score_to_confidence(score)

    return CategorizationResult(
        category=category,
        confidence=confidence,
        rationale=[
            f"Matched {score} keyword(s) associated with '{category}'."
        ],
    )


# ----------------------------------
# Internal Helpers
# ----------------------------------

def _normalize_text(vendor: Optional[str], raw_text: str) -> str:
    components = [
        vendor or "",
        raw_text or "",
    ]
    return " ".join(components).lower()


def _match_keywords(text: str, keywords: set[str]) -> int:
    return sum(1 for keyword in keywords if keyword in text)


def _score_to_confidence(score: int) -> Decimal:
    """
    Convert raw keyword match count to a bounded confidence score.
    """
    if score >= 4:
        return Decimal("0.95")
    if score == 3:
        return Decimal("0.85")
    if score == 2:
        return Decimal("0.70")
    if score == 1:
        return Decimal("0.55")
    return Decimal("0.00")
