from decimal import Decimal

# Confidence & Risk Thresholds
MIN_CONFIDENCE_SCORE = Decimal("0.65")
HIGH_RISK_LEVELS = {"HIGH", "VERY_HIGH"}

# Scenario Modes
SCENARIO_BASELINE = "baseline"
SCENARIO_CONSERVATIVE = "conservative"
SCENARIO_AGGRESSIVE = "aggressive"

# Tax System Constants
MAX_STANDARD_DEDUCTION_RATIO = Decimal("0.9")

# Explainability
MAX_REASONING_ITEMS = 10

# ML
DEFAULT_MODEL_VERSION = "v1.0"
ML_CONFIDENCE_FLOOR = Decimal("0.55")

# Audit
MAX_AUDIT_MESSAGE_LENGTH = 500

