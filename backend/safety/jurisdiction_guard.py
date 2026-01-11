class JurisdictionGuard:
    def validate(
        self,
        rule_jurisdiction: str,
        rule_year: int,
        user_jurisdiction: str,
        user_year: int,
    ) -> None:
        if rule_jurisdiction != user_jurisdiction:
            raise ValueError("Jurisdiction mismatch")

        if rule_year != user_year:
            raise ValueError("Tax year mismatch")
