# backend/data/deduplicator.py
import hashlib

def fingerprint(merchant: str, amount: float, date: str) -> str:
    raw = f"{merchant}-{amount}-{date}"
    return hashlib.sha256(raw.encode()).hexdigest()

def is_duplicate(fp: str, existing_fingerprints: set[str]) -> bool:
    return fp in existing_fingerprints
