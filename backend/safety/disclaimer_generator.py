# disclaimer_generator.py
from datetime import datetime

class DisclaimerGenerator:
    """
    Generates dynamic disclaimers for safety, legal, and finance contexts.
    """

    BASE_TEMPLATE = (
        "DISCLAIMER: This system is provided 'as-is' and is for informational purposes only. "
        "Users are responsible for compliance with local laws and regulations. "
        "Generated on {date}."
    )

    @staticmethod
    def generate(custom_text: str = "") -> str:
        """
        Generate a full disclaimer with optional custom text.
        """
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_disclaimer = DisclaimerGenerator.BASE_TEMPLATE.format(date=date)
        if custom_text:
            full_disclaimer += f" {custom_text}"
        return full_disclaimer
