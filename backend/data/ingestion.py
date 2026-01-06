"""
ingestion.py

Enterprise-grade ingestion for tax data systems.
"""

from __future__ import annotations

import json
import hashlib
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, EmailStr, ValidationError

# ---------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------

logger = logging.getLogger("tax_engine.ingestion")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
formatter = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] %(name)s - %(message)s"
)
handler.setFormatter(formatter)
logger.addHandler(handler)

# ---------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------

SCHEMA_VERSION = "1.0.0"
HASH_ALGORITHM = "sha256"

# ---------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------

class IngestionError(Exception):
    pass

class ValidationFailed(IngestionError):
    pass

class DuplicateSubmission(IngestionError):
    pass

class PersistenceFailed(IngestionError):
    pass

# ---------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------

class UserTaxPayload(BaseModel):
    schema_version: str = Field(default=SCHEMA_VERSION)
    idempotency_key: str = Field(..., min_length=10)

    user_id: str = Field(..., min_length=5)
    email: EmailStr
    country: str = Field(..., min_length=2, max_length=2)
    tax_year: int = Field(..., ge=2000, le=datetime.utcnow().year)

    income: float = Field(..., ge=0)
    deductions: float = Field(default=0, ge=0)
