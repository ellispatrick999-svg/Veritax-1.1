from enum import Enum

class ForbiddenAction(Enum):
    FINALIZE_FILING = "finalize_filing"
    GUARANTEE_LEGALITY = "guarantee_legality"
    OVERRIDE_USER = "override_user"
    PROVIDE_LEGAL_ADVICE = "provide_legal_advice"


class DecisionLimits:
    """
    Hard boundaries on what the AI system can do.
    """

    def __init__(self):
        self.forbidden = {action.value for action in ForbiddenAction}

    def check(self, action: str) -> None:
        if action in self.forbidden:
            raise PermissionError(
                f"Action '{action}' is not permitted by safety policy."
            )

    def allowed_actions(self) -> set[str]:
        return self.forbidden.copy()
