# app/agents/state.py
from langchain.agents import AgentState
from typing_extensions import NotRequired

class NutritionAgentState(AgentState):
    risk_level: NotRequired[str]             
    risk_reasons: NotRequired[list[str]]
    tool_budget_remaining: NotRequired[int]
    model_call_count: NotRequired[int]
    last_model_call_tokens: NotRequired[int]
    user_goal_locked: NotRequired[bool]
    supplement_review_required: NotRequired[bool]
    final_output_checked: NotRequired[bool]
    audit_events: NotRequired[list[dict]]