from dataclasses import dataclass


@dataclass
class Form1099:
    payer: str
    amount: float
    category: str
