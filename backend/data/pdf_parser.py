"""
pdf_parser.py

Extracts structured tax data from PDF documents.
Designed for compliance-grade ingestion pipelines.
"""

from __future__ import annotations

import re
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

import pdfplumber

# ---------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------

logger = logging.getLogger("tax_engine.pdf_parser")
logger.setLevel(logging.INFO)

# ---------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------

class PDFParsingError(Exception):
    pass

class UnsupportedPDFError(PDFParsingError):
    pass

# ---------------------------------------------------------------------
# Extracted Field Representation
# ---------------------------------------------------------------------

@dataclass
class ExtractedField:
    value: Optional[str]
    confidence: float  # 0.0 – 1.0
    source: str        # regex | anchor | heuristic

# ---------------------------------------------------------------------
# Regex Patterns (Conservative)
# ---------------------------------------------------------------------

PATTERNS = {
    "email": re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"),
    "tax_year": re.compile(r"(20\d{2})"),
    "income": re.compile(r"(?:total income|wages|income)[^\d]{0,10}([\d,]+\.\d{2})", re.I),
    "deductions": re.compile(r"(?:deductions|withheld)[^\d]{0,10}([\d,]+\.\d{2})", re.I),
    "user_id": re.compile(r"(?:SSN|Tax ID|User ID)[^\d]{0,10}([\w-]+)", re.I),
}

# ---------------------------------------------------------------------
# Core PDF Text Extraction
# ---------------------------------------------------------------------

def extract_text(pdf_path: str) -> str:
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if not pdf.pages:
                raise UnsupportedPDFError("PDF contains no pages")

            text = []
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text.append(page_text)

            if not text:
                raise UnsupportedPDFError("No extractable text found")

            return "\n".join(text)

    except Exception as exc:
        raise PDFParsingError(str(exc)) from exc

# ---------------------------------------------------------------------
# Field Extraction Helpers
# ---------------------------------------------------------------------

def extract_with_regex(pattern: re.Pattern, text: str) -> ExtractedField:
    match = pattern.search(text)
    if not match:
        return ExtractedField(None, 0.0, "regex")

    return ExtractedField(match.group(1), 0.85, "regex")

def extract_country(text: str) -> ExtractedField:
    if "UNITED STATES" in text.upper():
        return ExtractedField("US", 0.9, "heuristic")
    if "UNITED KINGDOM" in text.upper():
        return ExtractedField("GB", 0.9, "heuristic")

    return ExtractedField(None, 0.0, "heuristic")

# ---------------------------------------------------------------------
# Normalization
# ---------------------------------------------------------------------

def normalize_currency(value: Optional[str]) -> Optional[float]:
    if value is None:
        return None
    return float(value.replace(",", ""))

# ---------------------------------------------------------------------
# Main Extraction Logic
# ---------------------------------------------------------------------

def extract_tax_data(pdf_path: str) -> Dict[str, Any]:
    """
    Extract tax-relevant fields from a PDF.
    Returns structured data + confidence metadata.
    """

    logger.info("Starting PDF extraction", extra={"file": pdf_path})

    text = extract_text(pdf_path)

    extracted = {
        "email": extract_with_regex(PATTERNS["email"], text),
        "tax_year": extract_with_regex(PATTERNS["tax_year"], text),
        "income": extract_with_regex(PATTERNS["income"], text),
        "deductions": extract_with_regex(PATTERNS["deductions"], text),
        "user_id": extract_with_regex(PATTERNS["user_id"], text),
        "country": extract_country(text),
    }

    # Normalized output (ready for validation.py)
    payload = {
        "email": extracted["email"].value,
        "tax_year": int(extracted["tax_year"].value) if extracted["tax_year"].value else None,
        "income": normalize_currency(extracted["income"].value),
        "deductions": normalize_currency(extracted["deductions"].value),
        "user_id": extracted["user_id"].value,
        "country": extracted["country"].value,
    }

    # Confidence report (for audit & rejection logic)
    confidence = {
        field: extracted[field].confidence
        for field in extracted
    }

    logger.info(
        "PDF extraction completed",
        extra={
            "file": pdf_path,
            "confidence": confidence,
        },
    )

    return {
        "payload": payload,
        "confidence": confidence,
        "raw_text_hash": hash(text),
    }
