BLOCKED_PHRASES = {
    "ignore previous rules",
    "bypass safety",
    "act as a lawyer",
}

def sanitize(prompt: str) -> str:
    cleaned = prompt
    for phrase in BLOCKED_PHRASES:
        cleaned = cleaned.replace(phrase, "")
    return cleaned.strip()
