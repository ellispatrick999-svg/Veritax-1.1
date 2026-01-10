"""
ocr_processor.py

High-quality OCR processor for receipt ingestion in a tax engine.
Designed for accuracy, extensibility, and clean integration with
financial data pipelines.

Requirements:
- pytesseract
- opencv-python
- pillow
- numpy
- Tesseract OCR installed on system

Author: Your Company / Tax Engine Team
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional, Dict, Any

import cv2
import numpy as np
import pytesseract
from PIL import Image


# -----------------------------
# Configuration
# -----------------------------

TESSERACT_CONFIG = (
    "--oem 3 "
    "--psm 6 "
    "-c preserve_interword_spaces=1"
)


# -----------------------------
# Data Models
# -----------------------------

@dataclass
class ReceiptData:
    """
    Structured receipt data extracted from OCR text.
    """
    vendor: Optional[str]
    date: Optional[str]
    total: Optional[float]
    tax: Optional[float]
    raw_text: str


# -----------------------------
# OCR Processor
# -----------------------------

class OCRProcessor:
    """
    OCR processor responsible for:
    - Image preprocessing
    - Text extraction
    - Basic receipt field parsing

    This class is intentionally stateless and thread-safe.
    """

    def process_image(self, image_path: str) -> ReceiptData:
        """
        Main entry point for receipt OCR.

        Args:
            image_path: Path to receipt image

        Returns:
            ReceiptData object with extracted fields
        """
        image = self._load_image(image_path)
        processed = self._preprocess_image(image)
        text = self._extract_text(processed)

        return self._parse_receipt_text(text)

    # -----------------------------
    # Image Handling
    # -----------------------------

    def _load_image(self, image_path: str) -> np.ndarray:
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Unable to load image: {image_path}")
        return image

    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Advanced preprocessing for OCR accuracy:
        - Grayscale
        - Noise reduction
        - Adaptive thresholding
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        denoised = cv2.bilateralFilter(gray, 9, 75, 75)

        thresh = cv2.adaptiveThreshold(
            denoised,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31,
            2
        )

        return thresh

    # -----------------------------
    # OCR
    # -----------------------------

    def _extract_text(self, image: np.ndarray) -> str:
        """
        Extract raw text from preprocessed image.
        """
        pil_image = Image.fromarray(image)
        text = pytesseract.image_to_string(
            pil_image,
            config=TESSERACT_CONFIG
        )
        return text.strip()

    # -----------------------------
    # Parsing Logic
    # -----------------------------

    def _parse_receipt_text(self, text: str) -> ReceiptData:
        """
        Extract structured financial data from OCR text.
        """
        vendor = self._extract_vendor(text)
        date = self._extract_date(text)
        total = self._extract_total(text)
        tax = self._extract_tax(text)

        return ReceiptData(
            vendor=vendor,
            date=date,
            total=total,
            tax=tax,
            raw_text=text
        )

    # -----------------------------
    # Field Extractors
    # -----------------------------

    def _extract_vendor(self, text: str) -> Optional[str]:
        """
        Heuristic: vendor is often the first non-empty line.
        """
        for line in text.splitlines():
            clean = line.strip()
            if len(clean) > 3 and not re.search(r"\d", clean):
                return clean
        return None

    def _extract_date(self, text: str) -> Optional[str]:
        """
        Matches common receipt date formats.
        """
        date_patterns = [
            r"\b\d{2}/\d{2}/\d{4}\b",
            r"\b\d{4}-\d{2}-\d{2}\b",
            r"\b\d{2}-\d{2}-\d{4}\b",
        ]

        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group()

        return None

    def _extract_total(self, text: str) -> Optional[float]:
        """
        Extract total amount using common receipt keywords.
        """
        total_patterns = [
            r"total\s*\$?\s*([\d,.]+)",
            r"amount\s*due\s*\$?\s*([\d,.]+)",
            r"balance\s*\$?\s*([\d,.]+)"
        ]

        return self._extract_currency_value(text, total_patterns)

    def _extract_tax(self, text: str) -> Optional[float]:
        """
        Extract tax amount if present.
        """
        tax_patterns = [
            r"tax\s*\$?\s*([\d,.]+)",
            r"sales\s*tax\s*\$?\s*([\d,.]+)"
        ]

        return self._extract_currency_value(text, tax_patterns)

    def _extract_currency_value(
        self,
        text: str,
        patterns: list[str]
    ) -> Optional[float]:
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1).replace(",", "")
                try:
                    return float(value)
                except ValueError:
                    return None
        return None
