# strategy_context.py

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class StrategyContext:
    """
    A unified context object shared across all strategies.
    Normalizes and enriches raw context data.
    """

    tax_year: int
    filing_status: Optional[str] = None
    state: Optional[str] = None

    # IRS data, limits, deadlines, etc.
    irs_limits: Dict[str, Any] = field(default_factory=dict)
    irs_deadlines: Dict[str, Any] = field(default_factory=dict)

    # Market and economic data
    market_data: Dict[str, Any] = field(default_factory=dict)
    economic_assumptions: Dict[str, Any] = field(default_factory=dict)

    # System-level configuration
    config: Dict[str, Any] = field(default_factory=dict)

    # Raw context passed in by the caller
    raw: Dict[str, Any] = field(default_factory=dict)

    def get_limit(self, key: str, default: Any = None) -> Any:
        """Retrieve an IRS limit safely."""
        return self.irs_limits.get(key, default)

    def get_deadline(self, key: str, default: Any = None) -> Any:
        """Retrieve an IRS deadline safely."""
        return self.irs_deadlines.get(key, default)

    def get_market_value(self, symbol: str, default: Any = None) -> Any:
        """Retrieve market data for a given ticker."""
        return self.market_data.get(symbol, default)

    def get_config(self, key: str, default: Any = None) -> Any:
        """Retrieve system configuration values."""
        return self.config.get(key, default)

    @classmethod
    def from_raw(cls, raw_context: Dict[str, Any]) -> "StrategyContext":
        """
        Factory method that builds a StrategyContext from raw input.
        This is where normalization and defaulting happens.
        """

        return cls(
            tax_year=raw_context.get("tax_year"),
            filing_status=raw_context.get("filing_status"),
            state=raw_context.get("state"),

            irs_limits=raw_context.get("irs_limits", {}),
            irs_deadlines=raw_context.get("irs_deadlines", {}),

            market_data=raw_context.get("market_data", {}),
            economic_assumptions=raw_context.get("economic_assumptions", {}),

            config=raw_context.get("config", {}),

            raw=raw_context
        )
