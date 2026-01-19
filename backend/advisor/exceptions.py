class AdvisorError(Exception):
    """Base class for all advisor-related errors."""
    pass


class ValidationError(AdvisorError):
    """Raised when user input or derived data is invalid."""
    pass


class ComplianceError(AdvisorError):
    """Raised when advice violates compliance or regulatory rules."""
    pass


class RiskThresholdError(AdvisorError):
    """Raised when a strategy exceeds acceptable risk."""
    pass


class ScenarioError(AdvisorError):
    """Raised when scenario simulation fails."""
    pass


class ExplainabilityError(AdvisorError):
    """Raised when an explanation cannot be generated."""
    pass


class ModelUnavailableError(AdvisorError):
    """Raised when ML models are unavailable or invalid."""
    pass
