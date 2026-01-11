BANNED_PATTERNS = {
    "hide income",
    "fake expense",
    "avoid reporting",
    "evade taxes",
}

def detect_misuse(text: str) -> bool:
    lowered = text.lower()
    return any(pattern in lowered for pattern in BANNED_PATTERNS)
