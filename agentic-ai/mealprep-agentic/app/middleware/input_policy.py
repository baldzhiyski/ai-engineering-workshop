# app/middleware/input_policy.py
from typing import Any
from langchain.agents.middleware import before_agent
from langgraph.runtime import Runtime
from ..context import AppContext
from ..agents.state import NutritionAgentState

@before_agent(state_schema=NutritionAgentState)
def classify_request_risk(
    state: NutritionAgentState,
    runtime: Runtime[AppContext],
) -> dict[str, Any] | None:
    last_user = ""
    for msg in reversed(state["messages"]):
        if getattr(msg, "type", None) == "human":
            last_user = str(msg.content).lower()
            break

    risk_reasons = []
    risk_level = "low"

    risky_terms = [
        "prescribe",
        "diagnose",
        "replace my medication",
        "extreme calorie deficit",
        "megadose",
        "unsafe supplement stack",
    ]
    if any(term in last_user for term in risky_terms):
        risk_level = "high"
        risk_reasons.append("unsafe_or_medical_request")

    if "warfarin" in last_user or "insulin" in last_user:
        risk_level = "high"
        risk_reasons.append("high_risk_medication_mentioned")

    if "supplement" in last_user or "vitamin" in last_user:
        risk_reasons.append("supplement_related")

    return {
        "risk_level": risk_level,
        "risk_reasons": risk_reasons,
        "supplement_review_required": "supplement_related" in risk_reasons,
        "tool_budget_remaining": 10,
        "audit_events": [{"event": "request_classified", "risk_level": risk_level}],
    }