"""
validation.py

CPA-grade validation engine for receipt and tax data.
Ensures completeness, correctness, and audit readiness
according to IRS substantiation principles.

This module must never mutate input data.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Iterable, List, Optional
from datetime import datetime


# ----------------------------------
# Validation Models
# ----------------------------------

@dataclass(frozen=True)
class ValidationError:
    """
    Represents a single validation failure.
    """
    field: str
    code: str
    message: str
    severity: str  # ERROR | WARNING


@dataclass(frozen=True)
class ValidationResult:
    """
    Result of validating a financial record.
    """
    is_valid: bool
    errors: List[ValidationError]


# ----------------------------------
# Validation Constants
# ----------------------------------

REQUIRED_RECEIPT_FIELDS = {
    "vendor",
    "date",
    "total",
}

MAX_RECEIPT_AGE_YEARS = 7  # IRS record retention guideline


# ----------------------------------
# Public API
# ----------------------------------

def validate_receipt(receipt) -> ValidationResult:
    """
    Validate a parsed receipt object for CPA-grade compliance.

    Expected receipt attributes:
    - vendor: Optional[str]
    - date: Optional[str | datetime]
    - total: Optional[Decimal | float]
    - tax: Optional[Decimal | float]

    Returns:
        ValidationResult
    """
    errors: List[ValidationError] = []

    _validate_required_fields(receipt, errors)
    _validate_vendor(receipt.vendor, errors)
    _validate_date(receipt.date, errors)
    _validate_amount(receipt.total, "total", errors)
    _validate_amount(receipt.tax, "tax", errors, allow_none=True)

    return ValidationResult(
        is_valid=not any(e.severity == "ERROR" for e in errors),
        errors=errors,
    )


# ----------------------------------
# Validation Rules
# ----------------------------------

def _validate_required_fields(receipt, errors: List[ValidationError]) -> None:
    for field in REQUIRED_RECEIPT_FIELDS:
        if getattr(receipt, field, None) in (None, "", []):
            errors.append(
                ValidationError(
                    field=field,
                    code="REQUIRED_FIELD_MISSING",
                    message=f"Required field '{field}' is missing.",
                    severity="ERROR",
                )
            )


def _validate_vendor(vendor: Optional[str], errors: List[ValidationError]) -> None:
    if vendor is None:
        return

    if len(vendor.strip()) < 2:
        errors.append(
            ValidationError(
                field="vendor",
                code="INVALID_VENDOR",
                message="Vendor name is too short to be valid.",
                severity="ERROR",
            )
        )


def _validate_date(date_value, errors: List[ValidationError]) -> None:
    if date_value is None:
        return

    parsed_date: Optional[datetime] = None

    if isinstance(date_value, datetime):
        parsed_date = date_value
    elif isinstance(date_value, str):
        for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m-%d-%Y"):
            try:
                parsed_date = datetime.strptime(date_value, fmt)
                break
            except ValueError:
                continue

    if parsed_date is None:
        errors.append(
            ValidationError(
                field="date",
                code="INVALID_DATE_FORMAT",
                message="Date format is invalid or unsupported.",
                severity="ERROR",
            )
        )
        return

    if parsed_date > datetime.utcnow():
        errors.append(
            ValidationError(
                field="date",
                code="DATE_IN_FUTURE",
                message="Receipt date cannot be in the future.",
                severity="ERROR",
            )
        )

    years_old = (datetime.utcnow() - parsed_date).days / 365.25
    if years_old > MAX_RECEIPT_AGE_YEARS:
        errors.append(
            ValidationError(
                field="date",
                code="DATE_TOO_OLD",
                message="Receipt exceeds IRS record retention guidance.",
                severity="WARNING",
            )
        )


def _validate_amount(
    amount,
    field_name: str,
    errors: List[ValidationError],
    allow_none: bool = False,
) -> None:
    if amount is None:
        if allow_none:
            return
        errors.append(
            ValidationError(
                field=field_name,
                code="AMOUNT_MISSING",
                message=f"'{field_name}' amount is required.",
                severity="ERROR",
            )
        )
        return

    try:
        value = Decimal(str(amount))
    except (InvalidOperation, TypeError):
        errors.append(
            ValidationError(
                field=field_name,
                code="INVALID_AMOUNT",
                message=f"'{field_name}' must be a valid number.",
                severity="ERROR",
            )
        )
        return

    if value <= 0:
        errors.append(
            ValidationError(
                field=field_name,
                code="NON_POSITIVE_AMOUNT",
                message=f"'{field_name}' must be greater than zero.",
                severity="ERROR",
            )
        )

    if value > Decimal("1000000"):
        errors.append(
            ValidationError(
                field=field_name,
                code="AMOUNT_OUT_OF_RANGE",
                message=f"'{field_name}' amount is unusually large.",
                severity="WARNING",
            )
        )
