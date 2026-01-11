SENSITIVE_FIELDS = {
    "ssn",
    "ein",
    "bank_account",
    "routing_number",
}

def redact_payload(payload: dict) -> dict:
    redacted = {}
    for key, value in payload.items():
        if key.lower() in SENSITIVE_FIELDS:
            redacted[key] = "***REDACTED***"
        else:
            redacted[key] = value
    return redacted
