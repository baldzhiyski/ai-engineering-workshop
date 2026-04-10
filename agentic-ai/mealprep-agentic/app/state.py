# app/state.py
from __future__ import annotations

import operator
from typing import Annotated, TypedDict, Literal, Any
from langchain.messages import AnyMessage

class AppState(TypedDict, total=False):
    messages: Annotated[list[AnyMessage], operator.add]
    user_profile: dict
    retrieved_memories: list[dict]
    domain_context: list[str]
    macro_targets: dict
    plan_outline: dict
    nutrition_audit: dict
    grocery_optimization: dict
    final_plan: dict
    risk_flags: Annotated[list[str], operator.add]
    approval_required: bool
    approval_status: Literal["pending", "approved", "rejected"]
    errors: Annotated[list[str], operator.add]
    telemetry: dict[str, Any]