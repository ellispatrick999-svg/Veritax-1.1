# backend/data/enrichment.py
from backend.data.schema import FinancialRecord

DEDUCTIBLE_CATEGORIES = {
    "office_supplies",
    "software",
    "travel",
    "meals",
}

def enrich(record: FinancialRecord) -> FinancialRecord:
    record.deductible = record.category in DEDUCTIBLE_CATEGORIES
    return record
