# app/middleware/output_guardrails.py
from typing import Any
from langchain.agents.middleware import after_model
from langgraph.runtime import Runtime
from ..context import AppContext
from ..agents.state import NutritionAgentState

@after_model(state_schema=NutritionAgentState)
def validate_latest_ai_output(
    state: NutritionAgentState,
    runtime: Runtime[AppContext],
) -> dict[str, Any] | None:
    last = state["messages"][-1]
    text = str(last.content).lower()

    bad_phrases = [
        "replace your medication",
        "this cures",
        "guaranteed fat loss",
        "medical treatment plan",
    ]
    if any(p in text for p in bad_phrases):
        return {
            "risk_level": "high",
            "risk_reasons": state.get("risk_reasons", []) + ["unsafe_output_language"],
            "final_output_checked": False,
        }

    return {"final_output_checked": True}