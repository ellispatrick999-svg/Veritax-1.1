class UserConsent:
    def __init__(self):
        self._consents: dict[str, bool] = {}

    def grant(self, consent_type: str):
        self._consents[consent_type] = True

    def revoke(self, consent_type: str):
        self._consents[consent_type] = False

    def check(self, consent_type: str) -> bool:
        return self._consents.get(consent_type, False)
