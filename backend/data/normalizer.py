# backend/data/normalizer.py
import re
from datetime import datetime
from typing import Optional

def normalize_currency(value: str) -> float:
    cleaned = re.sub(r"[^\d.]", "", value)
    return float(cleaned) if cleaned else 0.0

def normalize_date(value: str) -> Optional[datetime.date]:
    for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%m/%d/%y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None

def normalize_merchant(value: str) -> str:
    return value.strip().title()
