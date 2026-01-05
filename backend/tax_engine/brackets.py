"""
brackets.py

A simple module for calculating progressive taxes.

Each tax bracket applies only to the income portion within that bracket.
"""

from typing import List, Tuple


# Type alias for clarity
# Each bracket is (upper_limit, tax_rate)
# upper_limit is None for the top bracket
TaxBracket = Tuple[float | None, float]


def calculate_progressive_tax(income: float, brackets: List[TaxBracket]) -> float:
    """
    Calculate total tax owed using progressive tax brackets.

    :param income: Total taxable income
    :param brackets: List of tax brackets (upper_limit, rate)
    :return: Total tax owed
    """
    if income <= 0:
        return 0.0

    tax = 0.0
    previous_limit = 0.0

    for upper_limit, rate in brackets:
        if upper_limit is None or income <= upper_limit:
            taxable_amount = income - previous_limit
            tax += taxable_amount * rate
            break
        else:
            taxable_amount = upper_limit - previous_limit
            tax += taxable_amount * rate
            previous_limit = upper_limit

    return round(tax, 2)


def calculate_effective_tax_rate(income: float, brackets: List[TaxBracket]) -> float:
    """
    Calculate the effective tax rate.

    :param income: Total taxable income
    :param brackets: List of tax brackets
    :return: Effective tax rate (0–1)
    """
    if income <= 0:
        return 0.0

    tax = calculate_progressive_tax(income, brackets)
    return round(tax / income, 4)


# Example brackets (you can change these)
DEFAULT_BRACKETS: List[TaxBracket] = [
    (10_000, 0.10),   # 10% up to 10,000
    (40_000, 0.20),   # 20% from 10,001–40,000
    (80_000, 0.30),   # 30% from 40,001–80,000
    (None, 0.40),     # 40% above 80,000
]


if __name__ == "__main__":
    # Example usage
    income = 75000

    tax = calculate_progressive_tax(income, DEFAULT_BRACKETS)
    effective_rate = calculate_effective_tax_rate(income, DEFAULT_BRACKETS)

    print(f"Income: ${income:,.2f}")
    print(f"Tax owed: ${tax:,.2f}")
    print(f"Effective tax rate: {effective_rate * 100:.2f}%")
