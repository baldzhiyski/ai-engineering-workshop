# app/state.py
from __future__ import annotations

import operator
from typing import Annotated, TypedDict, Literal, Any
from langchain.messages import AnyMessage
from typing import Annotated, Any, Literal
from typing_extensions import TypedDict
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


class AppState(TypedDict, total=False):
    messages: Annotated[list[AnyMessage], add_messages]

    user_profile: dict
    retrieved_memories: list[dict]
    domain_context: list[str]
    macro_targets: dict

    plan_outline: dict
    nutrition_audit: dict
    grocery_optimization: dict
    final_plan: dict

    risk_flags: list[str]
    approval_required: bool
    approval_status: Literal["pending", "approved", "revise", "rejected"]
    errors: list[str]
    reviewer_feedback: list[str]

    revision_count: int
    max_revisions: int

    telemetry: dict[str, Any]