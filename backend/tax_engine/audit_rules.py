from dataclasses import dataclass
from typing import Dict, List, Optional


# =====================================================
# DATA MODELS
# =====================================================

@dataclass
class AuditFlag:
    code: str
    description: str
    severity: int  # 1–10
    score_impact: int


@dataclass
class AuditResult:
    total_score: int
    flags: List[AuditFlag]
    risk_level: str


# =====================================================
# CORE RISK ENGINE
# =====================================================

class AuditRiskEngine:
    def __init__(self, config: Dict):
        self.config = config
        self.flags: List[AuditFlag] = []

    def add_flag(
        self,
        code: str,
        description: str,
        severity: int,
        score_impact: int
    ):
        self.flags.append(
            AuditFlag(
                code=code,
                description=description,
                severity=severity,
                score_impact=score_impact
            )
        )

    # =================================================
    # RULES — DEPRECIATION
    # =================================================

    def rule_excessive_section179(self, assets: List[Dict]):
        limit = self.config.get("section179_soft_limit", 1_000_000)
        total_179 = sum(a.get("section179", 0) for a in assets)

        if total_179 > limit:
            self.add_flag(
                code="DEP179_HIGH",
                description="Section 179 deduction unusually high",
                severity=8,
                score_impact=20
            )

    def rule_bonus_depreciation_heavy(self, assets: List[Dict]):
        bonus_total = sum(a.get("bonus", 0) for a in assets)
        cost_total = sum(a.get("cost", 0) for a in assets)

        if cost_total > 0 and bonus_total / cost_total > 0.8:
            self.add_flag(
                code="BONUS_HEAVY",
                description="Bonus depreciation exceeds 80% of asset cost",
                severity=6,
                score_impact=15
            )

    def rule_short_lived_assets(self, assets: List[Dict]):
        for a in assets:
            schedule = a.get("schedule", [])
            if len(schedule) <= 3:
                self.add_flag(
                    code="SHORT_RECOVERY",
                    description="High concentration of short recovery assets",
                    severity=5,
                    score_impact=10
                )
                break

    # =================================================
    # RULES — CONSISTENCY / BEHAVIORAL
    # =================================================

    def rule_large_year_over_year_change(
        self,
        prior_year_depreciation: Optional[float],
        current_year_depreciation: float
    ):
        if prior_year_depreciation is None:
            return

        if prior_year_depreciation == 0:
            return

        change_ratio = (
            current_year_depreciation / prior_year_depreciation
        )

        if change_ratio > 2.5:
            self.add_flag(
                code="YOY_SPIKE",
                description="Depreciation expense increased sharply year-over-year",
                severity=7,
                score_impact=18
            )

    # =================================================
    # RULES — STATE VS FEDERAL
    # =================================================

    def rule_state_federal_mismatch(
        self,
        federal_total: float,
        state_total: float
    ):
        if federal_total == 0:
            return

        diff_ratio = abs(federal_total - state_total) / federal_total

        if diff_ratio > 0.5:
            self.add_flag(
                code="STATE_MISMATCH",
                description="Large divergence between federal and state depreciation",
                severity=6,
                score_impact=12
            )

    # =================================================
    # FINAL SCORING
    # =================================================

    def score(self) -> AuditResult:
        total = sum(f.score_impact for f in self.flags)
        capped = min(100, total)

        if capped < 25:
            level = "LOW"
        elif capped < 50:
            level = "MODERATE"
        elif capped < 75:
            level = "HIGH"
        else:
            level = "SEVERE"

        return AuditResult(
            total_score=capped,
            flags=self.flags,
            risk_level=level
        )


# =====================================================
# HIGH-LEVEL API
# =====================================================

def run_audit(
    federal_assets: List[Dict],
    state_assets: List[Dict],
    config: Dict,
    prior_year_depreciation: Optional[float] = None
) -> AuditResult:

    engine = AuditRiskEngine(config)

    engine.rule_excessive_section179(federal_assets)
    engine.rule_bonus_depreciation_heavy(federal_assets)
    engine.rule_short_lived_assets(federal_assets)

    federal_total = sum(
        sum(a.get("schedule", [])) + a.get("section179", 0) + a.get("bonus", 0)
        for a in federal_assets
    )

    state_total = sum(
        sum(a.get("schedule", [])) + a.get("section179", 0) + a.get("bonus", 0)
        for a in state_assets
    )

    engine.rule_large_year_over_year_change(
        prior_year_depreciation,
        federal_total
    )

    engine.rule_state_federal_mismatch(
        federal_total,
        state_total
    )

    return engine.score()
