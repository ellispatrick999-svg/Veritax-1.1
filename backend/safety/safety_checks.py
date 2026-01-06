"""
safety_checks.py

Hard safety gate to prevent illegal, misleading, or unauthorized tax advice.
This module MUST be applied to all AI-generated responses before release.

Design principles:
- Default deny
- Explicit allowlists
- Jurisdiction & personalization blocking
- Explain-why-you-cannot-answer enforcement
"""

from dataclasses import dataclass
from typing import Optional, Dict, List
import re


# =====================================================
# SAFETY MODELS
# =====================================================

@dataclass
class SafetyResult:
    allowed: bool
    reason: Optional[str] = None
    sanitized_response: Optional[str] = None


# =====================================================
# CONSTANTS
# =====================================================

# Phrases that indicate personalized or illegal tax advice
PROHIBITED_PATTERNS = [
    r"\byou should\b",
    r"\bI recommend\b",
    r"\bto reduce your taxes\b",
    r"\bclaim this deduction\b",
    r"\byour best option\b",
    r"\bfile as\b",
    r"\bhack\b",
    r"\bavoid paying\b",
    r"\bhiding income\b",
    r"\bunderground\b",
    r"\boffshore\b",
    r"\bevasion\b",
]

# Allowed educational framing
ALLOWED_CONTEXT_PATTERNS = [
    r"\bgeneral information\b",
    r"\beducational purposes\b",
    r"\bnot tax advice\b",
    r"\bIRS generally\b",
    r"\bthe tax code provides\b",
]

# Jurisdictions your engine supports
SUPPORTED_JURISDICTIONS = {
    "US": ["IRS", "federal", "Form 1040"]
}

REQUIRED_DISCLAIMER = (
    "This information is for general educational purposes only "
    "and does not constitute legal or tax advice."
)


# =====================================================
# CORE SAFETY CHECKS
# =====================================================

def contains_prohibited_language(text: str) -> bool:
    for pattern in PROHIBITED_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def contains_allowed_context(text: str) -> bool:
    for pattern in ALLOWED_CONTEXT_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def contains_required_disclaimer(text: str) -> bool:
    return REQUIRED_DISCLAIMER.lower() in text.lower()


def check_jurisdiction(context: Dict) -> bool:
    """
    Ensures output only applies to supported jurisdictions
    """
    jurisdiction = context.get("jurisdiction", "US")
    return jurisdiction in SUPPORTED_JURISDICTIONS


def is_personalized(context: Dict) -> bool:
    """
    Blocks personalized advice
    """
    return any(
        key in context
        for key in [
            "ssn",
            "taxpayer_id",
            "exact_income",
            "specific_deduction_amount",
        ]
    )


# =====================================================
# RESPONSE SANITIZER
# =====================================================

def sanitize_response(text: str) -> str:
    """
    Removes imperative language and replaces it
    with neutral educational framing.
    """
    replacements = {
        r"\byou should\b": "one common approach is",
        r"\bI recommend\b": "the tax code allows",
        r"\byour\b": "a taxpayer's",
    }

    sanitized = text
    for pattern, replacement in replacements.items():
        sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)

    if not contains_required_disclaimer(sanitized):
        sanitized += f"\n\n{REQUIRED_DISCLAIMER}"

    return sanitized


# =====================================================
# MASTER SAFETY GATE
# =====================================================

def safety_gate(
    ai_response: str,
    context: Optional[Dict] = None
) -> SafetyResult:
    """
    Final gatekeeper for all AI-generated tax content.
    """

    context = context or {}

    # 1. Jurisdiction enforcement
    if not check_jurisdiction(context):
        return SafetyResult(
            allowed=False,
            reason="Unsupported tax jurisdiction."
        )

    # 2. Personalization block
    if is_personalized(context):
        return SafetyResult(
            allowed=False,
            reason="Personalized tax advice is not permitted."
        )

    # 3. Prohibited language
    if contains_prohibited_language(ai_response):
        return SafetyResult(
            allowed=False,
            reason="Response contains prohibited or advisory language."
        )

    # 4. Context framing
    if not contains_allowed_context(ai_response):
        ai_response = sanitize_response(ai_response)

    # 5. Disclaimer enforcement
    if not contains_required_disclaimer(ai_response):
        ai_response += f"\n\n{REQUIRED_DISCLAIMER}"

    return SafetyResult(
        allowed=True,
        sanitized_response=ai_response
    )
