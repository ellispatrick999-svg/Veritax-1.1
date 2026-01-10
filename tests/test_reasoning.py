import pytest
from ai_api import run_reasoning_engine

# --- Mock pipeline functions ---
# In a real system, these would be imported from your modules

def nlp_parser(question: str) -> dict:
    """
    Extract intent and entities from natural language.
    """
    # Mock example
    if "deduction" in question.lower():
        return {"intent": "deduction_check", "entities": {}}
    return {"intent": "general_inquiry", "entities": {}}

def build_context(user_context: dict) -> dict:
    """
    Enrich or normalize user context.
    """
    ctx = user_context.copy()
    ctx.setdefault("income", 0)
    ctx.setdefault("filing_status", "single")
    return ctx

def route_rules(intent: str, context: dict) -> str:
    """
    Decide which rule engine / tax logic to run.
    """
    routing_table = {
        "deduction_check": "deduction_rules",
        "general_inquiry": "general_rules"
    }
    return routing_table.get(intent, "fallback_rules")

def inference_engine(rule_path: str, context: dict) -> dict:
    """
    Mock deterministic + AI inference.
    """
    if rule_path == "deduction_rules":
        answer = f"You may qualify for standard deduction of {context.get('income', 0) * 0.12:.2f}"
    else:
        answer = "General tax guidance."
    reasoning_steps = [f"Applied {rule_path} based on context"]
    return {"answer": answer, "reasoning_steps": reasoning_steps, "confidence": 0.85}

def explain(inference_output: dict) -> str:
    """
    Build user-friendly explanation from reasoning.
    """
    steps = "\n".join(inference_output.get("reasoning_steps", []))
    return f"{inference_output['answer']}\nExplanation Steps:\n{steps}"


# --- Test Cases ---

def test_nlp_parser_detects_intent():
    question = "What deductions am I eligible for?"
    parsed = nlp_parser(question)
    assert parsed["intent"] == "deduction_check"
    assert isinstance(parsed["entities"], dict)

def test_build_context_normalizes_fields():
    user_context = {"income": 75000}
    ctx = build_context(user_context)
    assert ctx["income"] == 75000
    assert ctx["filing_status"] == "single"  # default set
    assert isinstance(ctx, dict)

def test_route_rules_selects_correct_path():
    context = {"income": 50000}
    intent = "deduction_check"
    path = route_rules(intent, context)
    assert path == "deduction_rules"

    path = route_rules("general_inquiry", context)
    assert path == "general_rules"

    path = route_rules("unknown_intent", context)
    assert path == "fallback_rules"

def test_inference_engine_outputs_expected_format():
    context = {"income": 60000}
    output = inference_engine("deduction_rules", context)
    assert "answer" in output
    assert "reasoning_steps" in output
    assert "confidence" in output
    assert 0.0 <= output["confidence"] <= 1.0

def test_explain_returns_human_readable_string():
    inference = {"answer": "You may qualify.", "reasoning_steps": ["Step1", "Step2"]}
    explanation = explain(inference)
    assert "You may qualify." in explanation
    assert "Step1" in explanation
    assert "Step2" in explanation

# --- End-to-end pipeline test ---

def test_full_reasoning_pipeline():
    question = "Am I eligible for standard deductions?"
    user_context = {"income": 85000}

    # 1. Parse
    parsed = nlp_parser(question)
    intent = parsed["intent"]
    entities = parsed["entities"]
    assert intent in ["deduction_check", "general_inquiry"]

    # 2. Build context
    context = build_context(user_context)
    assert "income" in context
    assert "filing_status" in context

    # 3. Route rules
    rule_path = route_rules(intent, context)
    assert isinstance(rule_path, str)

    # 4. Inference
    inference_output = inference_engine(rule_path, context)
    assert "answer" in inference_output
    assert "reasoning_steps" in inference_output
    assert "confidence" in inference_output

    # 5. Explanation
    explanation = explain(inference_output)
    assert isinstance(explanation, str)
    assert inference_output["answer"] in explanation
    for step in inference_output["reasoning_steps"]:
        assert step in explanation

    # 6. Optional: test ai_api integration
    api_output = run_reasoning_engine(question, user_context)
    assert "answer" in api_output
    assert "reasoning_steps" in api_output
    assert 0.0 <= api_output["confidence"] <= 1.0
