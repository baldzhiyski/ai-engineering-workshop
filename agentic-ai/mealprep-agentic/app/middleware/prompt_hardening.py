# app/middleware/prompt_hardening.py
from typing import Any
from langchain.agents.middleware import before_model
from langgraph.runtime import Runtime
from ..context import AppContext
from ..agents.state import NutritionAgentState

@before_model(state_schema=NutritionAgentState)
def add_risk_specific_instructions(
    state: NutritionAgentState,
    runtime: Runtime[AppContext],
) -> dict[str, Any] | None:
    risk = state.get("risk_level", "low")
    if risk != "high":
        return None

    extra = (
        "High-risk mode is active. "
        "Do not provide medical treatment advice. "
        "Do not recommend medication changes. "
        "Be conservative with supplements. "
        "If uncertainty exists, explicitly recommend clinician review."
    )

    messages = list(state["messages"])
    if messages:
        messages[0].content = f"{messages[0].content}\n\n{extra}"
        return {"messages": messages}
    return None