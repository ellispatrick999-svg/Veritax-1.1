"""
Explanation Generator for Tax AI

Purpose:
- Convert structured outputs into human-friendly, conversational text
- Highlight confidence, assumptions, and ambiguities
- Avoid giving advice or computed tax amounts
- Provide next steps or escalation suggestions
"""

from typing import List

from backend.ai.reasoning import ReasoningOutput, ConfidenceLevel
from backend.tax_engine.rule_router import RuleRoutingResult, RuleMatch
from backend.ai.context_builder import ContextBuildResult


def generate_context_summary(result: ContextBuildResult) -> str:
    """
    Generates a conversational summary of the user's context.
    """
    ctx = result.context
    lines: List[str] = [
        f"Let's review your tax profile for {ctx.tax_year}:",
        f"- Filing status: {ctx.filing_status.value.replace('_', ' ')}",
        f"- Income: ${ctx.income:,.0f}" if ctx.income else "- Income: Not provided",
        f"- Deductions: {', '.join(ctx.deductions.keys()) or 'None'}",
        f"- Dependents: {ctx.dependents}",
    ]

    if result.warnings:
        lines.append("\n⚠️ Warnings:")
        for w in result.warnings:
            lines.append(f"  • {w}")

    if result.notes:
        lines.append("\nℹ️ Notes:")
        for n in result.notes:
            lines.append(f"  • {n}")

    return "\n".join(lines)


def generate_rule_summary(rules: RuleRoutingResult) -> str:
    """
    Generates a conversational summary of applicable tax rules.
    """
    lines: List[str] = ["Based on your profile, the following tax rules may be relevant:"]

    if rules.applicable_rules:
        for r in rules.applicable_rules:
            lines.append(
                f" • {r.rule_id.replace('_', ' ')}: {r.description}. Reason: {r.reason_applied}"
            )
    else:
        lines.append(" • No specific rules could be identified from your profile.")

    if rules.excluded_rules:
        lines.append("\nRules that are likely not applicable:")
        for rid, reason in rules.excluded_rules.items():
            lines.append(f" • {rid.replace('_', ' ')}: {reason}")

    return "\n".join(lines)


def generate_reasoning_summary(reasoning: ReasoningOutput) -> str:
    """
    Converts reasoning outputs into a conversational summary.
    """
    lines: List[str] = [
        reasoning.summary,
        "",
        reasoning.explanation
    ]

    if reasoning.confidence == ConfidenceLevel.LOW:
        lines.append(
            "\n⚠️ The confidence in these interpretations is low. "
            "It may be helpful to double-check details or consult a professional."
        )
    elif reasoning.confidence == ConfidenceLevel.MEDIUM:
        lines.append(
            "\nℹ️ The confidence is moderate. Some amounts or assumptions may need review."
        )
    else:
        lines.append("\n✅ Confidence in the interpretation is high.")

    if reasoning.requires_human_review:
        lines.append(
            "⚠️ Certain items may benefit from review by a tax professional."
        )

    return "\n".join(lines)


def generate_full_explanation(
    context_result: ContextBuildResult,
    rule_result: RuleRoutingResult,
    reasoning_result: ReasoningOutput,
) -> str:
    """
    Combines context, rules, and reasoning into a single human-friendly explanation.
    """

    parts: List[str] = [
        "Hello! Here's a summary based on the information you provided:\n",
        generate_context_summary(context_result),
        "\n",
        generate_rule_summary(rule_result),
        "\n",
        generate_reasoning_summary(reasoning_result),
