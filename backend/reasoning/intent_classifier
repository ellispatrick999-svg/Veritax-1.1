"""
intent_classifier.py

Identifies user intent and optionally extracts high-level slots.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class IntentResult:
    """Structured result of intent classification."""
    intent: str
    confidence: float  # 0.0–1.0
    slots: Dict[str, Any]


class IntentClassifier:
    """
    Base intent classifier abstraction.

    You can:
    - Wrap an ML model
    - Call an external service
    - Implement rule-based classification

    Current implementation is a simple rule-based stub.
    """

    def __init__(self) -> None:
        # Inject or initialize models here (if needed).
        pass

    def classify(self, text: str) -> IntentResult:
        """
        Classify user input into an intent with confidence.

        Replace this stub with a real ML or LLM-based classifier.
        """
        lowered = text.lower()

        if any(keyword in lowered for keyword in ("help", "how do i", "can you explain")):
            intent = "request_explanation"
            confidence = 0.8
        elif any(keyword in lowered for keyword in ("remind me", "schedule", "set a reminder")):
            intent = "create_reminder"
            confidence = 0.75
        elif any(keyword in lowered for keyword in ("what is", "who is", "define")):
            intent = "knowledge_query"
            confidence = 0.7
        else:
            intent = "chitchat_or_unknown"
            confidence = 0.4

        return IntentResult(intent=intent, confidence=confidence, slots={})

    def classify_with_context(
        self,
        text: str,
        dialog_state: Optional[str] = None,
    ) -> IntentResult:
        """
        Optional context-aware classification that can adjust confidence or
        resolve ambiguous intents.
        """
        base_result = self.classify(text)

        # Example: if we are mid slot-filling, bias toward previous intent.
        if dialog_state == "COLLECTING_INFO" and base_result.confidence < 0.7:
            base_result.confidence += 0.1

        return base_result
