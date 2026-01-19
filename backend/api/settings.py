import os
from enum import Enum
from typing import Dict, Set


# =====================
# Environment Detection
# =====================

class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TEST = "test"


ENVIRONMENT: Environment = Environment(
    os.getenv("APP_ENV", Environment.DEVELOPMENT.value)
)


def is_production() -> bool:
    return ENVIRONMENT == Environment.PRODUCTION


def is_test() -> bool:
    return ENVIRONMENT == Environment.TEST


# =====================
# Feature Flags
# =====================

FEATURE_FLAGS: Dict[str, bool] = {
    "ENABLE_ADVISOR": True,
    "ENABLE_ML_SCORING": os.getenv("ENABLE_ML_SCORING", "false").lower() == "true",
    "ENABLE_SCENARIO_ENGINE": True,
    "ENABLE_EXPLAINABILITY": True,
    "ENABLE_AGGRESSIVE_STRATEGIES": not is_production(),
    "ENABLE_PARTNER_API": False,
}


def feature_enabled(flag: str) -> bool:
    return FEATURE_FLAGS.get(flag, False)


# =====================
# API Rate Limits
# =====================

API_RATE_LIMITS = {
    "default": {
        "requests": int(os.getenv("RATE_LIMIT_REQUESTS", 100)),
        "window_seconds": int(os.getenv("RATE_LIMIT_WINDOW", 60)),
    },
    "auth": {
        "requests": 20,
        "window_seconds": 60,
    },
}


# =====================
# Timeout Thresholds (seconds)
# =====================

TIMEOUTS = {
    "api_request": float(os.getenv("API_TIMEOUT", 5.0)),
    "tax_calculation": float(os.getenv("TAX_CALC_TIMEOUT", 3.0)),
    "advisor_pipeline": float(os.getenv("ADVISOR_TIMEOUT", 6.0)),
    "external_service": float(os.getenv("EXTERNAL_SERVICE_TIMEOUT", 4.0)),
}


# =====================
# External Service Config
# =====================

EXTERNAL_SERVICES = {
    "ai_provider": {
        "base_url": os.getenv("AI_API_URL", ""),
        "api_key": os.getenv("AI_API_KEY", ""),
        "enabled": bool(os.getenv("AI_API_KEY")),
    },
    "tax_data_provider": {
        "base_url": os.getenv("TAX_DATA_API_URL", ""),
        "api_key": os.getenv("TAX_DATA_API_KEY", ""),
        "enabled": bool(os.getenv("TAX_DATA_API_KEY")),
    },
}


# =====================
# Logging Configuration
# =====================

LOG_LEVEL = os.getenv(
    "LOG_LEVEL",
    "INFO" if is_production() else "DEBUG"
)

LOG_FORMAT = (
    "%(asctime)s | %(levelname)s | %(name)s | "
    "%(message)s"
)

ENABLE_REQUEST_LOGGING = not is_test()
ENABLE_AUDIT_LOGGING = is_production()


# =====================
# Jurisdiction Toggles
# =====================

SUPPORTED_JURISDICTIONS: Set[str] = {
    "US",
}

DEFAULT_JURISDICTION = os.getenv("DEFAULT_JURISDICTION", "US")

ALLOW_MULTI_JURISDICTION = False  # critical safety toggle


# =====================
# Compliance & Safety Thresholds
# =====================

CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", 0.65))
HIGH_RISK_REVIEW_REQUIRED = True

MAX_ACCEPTABLE_RISK_LEVEL = os.getenv(
    "MAX_RISK_LEVEL", "MEDIUM"
)


# =====================
# Security Settings
# =====================

REQUIRE_AUTHENTICATION = True
REQUIRE_CONSENT_FOR_ADVICE = True

TOKEN_EXPIRATION_SECONDS = int(
    os.getenv("TOKEN_EXPIRATION_SECONDS", 3600)
)


# =====================
# Testing Overrides
# =====================

if is_test():
    FEATURE_FLAGS["ENABLE_ML_SCORING"] = False
    FEATURE_FLAGS["ENABLE_AGGRESSIVE_STRATEGIES"] = False
    ENABLE_REQUEST_LOGGING = False

