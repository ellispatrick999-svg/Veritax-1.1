from dataclasses import dataclass


@dataclass
class W2:
    employer: str
    wages: float
    federal_tax_withheld: float
    state_tax_withheld: float
