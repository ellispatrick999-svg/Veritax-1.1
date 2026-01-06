"""
strategy_engine.py

Educational Tax Strategy Engine (Safe Version)
- Explains tax rules and deductions in general terms.
- Highlights publicly documented options like Section 179, bonus depreciation, standard/itemized deductions.
- Does NOT give personalized tax advice or suggest actions.
- Fully audit-safe and suitable for teaching.
"""

from typing import Dict, List


class StrategyEngine:
    def __init__(self):
        self.educational_notes: List[str] = []

    def analyze_return(self, irs_return: Dict) -> List[str]:
        """
        Analyze the IRS return and generate safe, educational notes about deductions and depreciation.
        """
        self.educational_notes.clear()
        forms = {f.get("Form"): f for f in irs_return.get("Forms", [])}

        # Section 179 (general info)
        if "4562" in forms:
            self.educational_notes.append(
                "Section 179 allows businesses to elect to expense certain property in the year placed in service. "
                "Limits are set by IRS annually."
            )

        # Bonus depreciation (general info)
        if "4562" in forms:
            self.educational_notes.append(
                "Bonus depreciation allows additional first-year depreciation for qualified property, "
                "subject to IRS rules."
            )

        # Standard vs itemized deductions
        if "1040" in forms:
            self.educational_notes.append(
                "Taxpayers can generally choose between standard or itemized deductions, depending on which is higher."
            )

        # Schedule C net loss info
        if "Schedule C" in forms:
            self.educational_notes.append(
                "Schedule C reports business income and expenses. Losses can affect taxable income calculations."
            )

        # W2/1099 overview
        if "W2" in forms or "1099-NEC" in forms:
            self.educational_notes.append(
                "W-2 and 1099 forms report wages and independent contractor income, respectively, used to calculate total income."
            )

        # General educational note about limits and compliance
        self.educational_notes.append(
            "All deductions, depreciation, and credits are subject to IRS rules and limits. Always ensure compliance."
        )

        return self.educational_notes


# =====================================================
# PUBLIC API
# =====================================================

def educational_notes(irs_return: Dict) -> List[str]:
    """
    Safe educational notes on the tax return.
    """
    engine = StrategyEngine()
    return engine.analyze_return(irs_return)


# =====================================================
# EXAMPLE USAGE
# =====================================================

if __name__ == "__main__":
    example_return = {
        "Forms": [
            {"Form": "1040", "Line 9": 100000, "Line 12": 12000},
            {"Form": "4562", "Part I Section 179": 25000, "Part II Bonus Depreciation": 15000},
            {"Form": "Schedule C", "Net Profit": 50000}
        ]
    }

    notes = educational_notes(example_return)
    print("=== EDUCATIONAL NOTES ===")
    for n in notes:
        print(f"- {n}")
