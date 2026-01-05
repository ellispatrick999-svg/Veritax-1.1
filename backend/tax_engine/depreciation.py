from dataclasses import dataclass
from typing import Dict, List, Optional
import json


# =====================================================
# CONFIG LOADING
# =====================================================

def load_tax_config(path: str) -> Dict:
    with open(path, "r") as f:
        return json.load(f)


# =====================================================
# MACRS TABLES — GDS HALF-YEAR
# =====================================================

MACRS_GDS_HALF_YEAR = {
    3:  [0.3333, 0.4445, 0.1481, 0.0741],
    5:  [0.20, 0.32, 0.192, 0.1152, 0.1152, 0.0576],
    7:  [0.1429, 0.2449, 0.1749, 0.1249, 0.0893, 0.0892, 0.0893, 0.0446],
    10: [0.10, 0.18, 0.144, 0.1152, 0.0922, 0.0737, 0.0655,
         0.0655, 0.0656, 0.0655, 0.0328],
    15: [0.05, 0.095, 0.0855, 0.077, 0.0693, 0.0623, 0.059,
         0.059, 0.0591, 0.059, 0.0591, 0.059,
         0.0591, 0.059, 0.0295],
    20: [0.0375, 0.0722, 0.0668, 0.0618, 0.0571, 0.0529,
         0.0489, 0.0452, 0.0446, 0.0446, 0.0446,
         0.0446, 0.0446, 0.0446, 0.0446, 0.0446,
         0.0446, 0.0446, 0.0446, 0.0446, 0.0223],
}


# =====================================================
# DATA MODELS
# =====================================================

@dataclass
class DepreciableAsset:
    cost: float
    recovery_period: int
    placed_in_service_qtr: int  # 1–4
    section179: float = 0.0
    use_ads: bool = False
    state_override: Optional[str] = None


@dataclass
class AssetPool:
    assets: List[DepreciableAsset]


# =====================================================
# SECTION 179
# =====================================================

def apply_section179(cost: float, elected: float) -> float:
    return round(cost - min(cost, elected), 2)


# =====================================================
# BONUS DEPRECIATION
# =====================================================

def bonus_depreciation(basis: float, rate: float) -> float:
    return round(basis * rate, 2)


# =====================================================
# MID-QUARTER TEST
# =====================================================

def requires_mid_quarter(assets: List[DepreciableAsset]) -> bool:
    total = sum(a.cost for a in assets)
    q4 = sum(a.cost for a in assets if a.placed_in_service_qtr == 4)
    return q4 / total > 0.40 if total else False


# =====================================================
# ADS (STRAIGHT-LINE)
# =====================================================

def ads_schedule(basis: float, recovery_period: int) -> List[float]:
    annual = round(basis / recovery_period, 2)
    schedule = [annual] * recovery_period
    schedule[-1] += round(basis - sum(schedule), 2)
    return schedule


# =====================================================
# MACRS SCHEDULE
# =====================================================

def macrs_schedule(basis: float, recovery_period: int) -> List[float]:
    rates = MACRS_GDS_HALF_YEAR[recovery_period]
    schedule = [round(basis * r, 2) for r in rates]
    schedule[-1] += round(basis - sum(schedule), 2)
    return schedule


# =====================================================
# FULL ASSET DEPRECIATION
# =====================================================

def depreciate_asset(
    asset: DepreciableAsset,
    bonus_rate: float,
    use_mid_quarter: bool = False
) -> Dict:

    # Section 179
    basis = apply_section179(asset.cost, asset.section179)

    # Bonus
    bonus = bonus_depreciation(basis, bonus_rate)
    basis -= bonus

    # MACRS or ADS
    if asset.use_ads:
        schedule = ads_schedule(basis, asset.recovery_period)
    else:
        schedule = macrs_schedule(basis, asset.recovery_period)

    return {
        "cost": asset.cost,
        "section179": min(asset.cost, asset.section179),
        "bonus": bonus,
        "remaining_basis": basis,
        "schedule": schedule,
        "total_depreciation": round(
            min(asset.cost, asset.section179) + bonus + sum(schedule), 2
        ),
    }


# =====================================================
# POOL DEPRECIATION (FEDERAL / STATE)
# =====================================================

def depreciate_pool(
    pool: AssetPool,
    tax_config: Dict
) -> Dict[str, List[Dict]]:

    mid_q = requires_mid_quarter(pool.assets)
    bonus_rate = tax_config["bonus_rate"]

    federal = []
    state = []

    for asset in pool.assets:
        federal.append(
            depreciate_asset(asset, bonus_rate, mid_q)
        )

        # State often disallows bonus/179
        state_bonus = tax_config.get("state_bonus_rate", 0.0)
        state.append(
            depreciate_asset(
                asset,
                state_bonus,
                mid_q
            )
        )

    return {
        "federal": federal,
        "state": state
    }
