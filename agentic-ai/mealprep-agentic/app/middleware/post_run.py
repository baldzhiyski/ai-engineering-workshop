# app/middleware/post_run.py
from typing import Any
from langchain.agents.middleware import after_agent
from langgraph.runtime import Runtime
from ..context import AppContext
from ..agents.state import NutritionAgentState

@after_agent(state_schema=NutritionAgentState)
def finalize_audit(
    state: NutritionAgentState,
    runtime: Runtime[AppContext],
) -> dict[str, Any] | None:
    audit = state.get("audit_events", [])
    audit.append({
        "event": "agent_completed",
        "risk_level": state.get("risk_level", "unknown"),
        "model_calls": state.get("model_call_count", 0),
    })
    return {"audit_events": audit}