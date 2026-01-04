"""
NLP Entity Parser for Tax & Financial Text

Purpose:
- Extract structured entities from user-provided natural language
- NEVER infer tax legality
- NEVER compute values
- ALWAYS attach confidence + provenance

Example input:
"I made about 85k last year and paid 4k in student loan interest."

Example output:
{
  income: 85000,
  deductions: {"student_loan_interest": 4000}
}
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional
import re


# -----------------------------
# Entity definitions
# -----------------------------

class EntityType(str, Enum):
    INCOME = "income"
    DEDUCTION = "deduction"
    DATE = "date"
    OTHER = "other"


@dataclass
class ExtractedEntity:
    type: EntityType
    value: str
    normalized_value: Optional[float]
    confidence: float
    source_text: str


@dataclass
class ParsedUserInput:
    raw_text: str
    entities: List[ExtractedEntity]
    warnings: List[str]


# -----------------------------
# Normalization helpers
# -----------------------------

_CURRENCY_RE = re.compile(
    r"\$?\s*([\d,]+(?:\.\d+)?)\s*(k|K|thousand)?"
)

_DEDUCTION_KEYWORDS = {
    "student loan": "student_loan_interest",
    "mortgage interest": "mortgage_interest",
    "charity": "charitable_donation",
    "donation": "charitable_donation",
    "home office": "home_office",
    "medical": "medical_expenses",
}


def _normalize_currency(match: re.Match) -> Optional[float]:
    try:
        number = float(match.group(1).replace(",", ""))
        multiplier = match.group(2)
        if multiplier:
            number *= 1000
        return number
    except Exception:
        return None


# -----------------------------
# Core parsing logic
# -----------------------------

def parse_user_text(text: str) -> ParsedUserInput:
    """
    Main NLP entry point.
    Extracts entities conservatively and transparently.
    """

    entities: List[ExtractedEntity] = []
    warnings: List[str] = []

    lowered = text.lower()

    # -------------------------
    # Income extraction
    # -------------------------
    if any(keyword in lowered for keyword in ["made", "earned", "income", "salary"]):
        for match in _CURRENCY_RE.finditer(text):
            value = _normalize_currency(match)
            if value:
                entities.append(
                    ExtractedEntity(
                        type=EntityType.INCOME,
                        value=match.group(0),
                        normalized_value=value,
                        confidence=0.75,
                        source_text=text,
                    )
                )
                break  # Only one income assumed

    # -------------------------
    # Deduction extraction
    # -------------------------
    for phrase, deduction_key in _DEDUCTION_KEYWORDS.items():
        if phrase in lowered:
            for match in _CURRENCY_RE.finditer(text):
                value = _normalize_currency(match)
                if value:
                    entities.append(
                        ExtractedEntity(
                            type=EntityType.DEDUCTION,
                            value=deduction_key,
                            normalized_value=value,
                            confidence=0.7,
                            source_text=text,
                        )
                    )
                    break

    # -------------------------
    # Ambiguity detection
    # -------------------------
    if not entities:
        warnings.append(
            "No confidently identifiable financial entities were found."
        )

    if "about" in lowered or "around" in lowered or "roughly" in lowered:
        warnings.append(
            "Some values appear to be estimates, not exact amounts."
        )
        for e in entities:
            e.confidence *= 0.85

    return ParsedUserInput(
        raw_text=text,
        entities=entities,
        warnings=warnings,
    )


# -----------------------------
# Structured output helper
# -----------------------------

def entities_to_financial_facts(
    parsed: ParsedUserInput,
) -> Dict[str, Dict[str, float]]:
    """
    Converts extracted entities into deterministic financial facts.
    Drops low-confidence entities.
    """

    income: Optional[float] = None
    deductions: Dict[str, float] = {}

    for entity in parsed.entities:
        if entity.confidence < 0.6:
            continue

        if entity.type == EntityType.INCOME and income is None:
            income = entity.normalized_value

        if entity.type == EntityType.DEDUCTION:
            deductions[entity.value] = entity.normalized_value

    return {
        "income": income,
        "deductions": deductions,
    }
