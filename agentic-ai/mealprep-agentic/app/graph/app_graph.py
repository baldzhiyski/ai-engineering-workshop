# app/graph/app_graph.py
from __future__ import annotations

import uuid
from langgraph.graph import StateGraph, START, END
from langgraph.runtime import Runtime
from langgraph.types import interrupt

from ..context import AppContext
from ..state import AppState
from ..domain.models import UserProfile
from ..services.nutrition_math import compute_macro_targets
from ..graph.weekly_planner_subgraph import build_weekly_plan_subgraph
from ..agents.validator import build_validator_agent
from ..agents.coach import build_coach_agent
from ..config import settings


def build_app_graph(*, store=None, checkpointer=None):
    weekly_plan_subgraph = build_weekly_plan_subgraph(
        store=store,
        checkpointer=checkpointer,
    )
    validator_agent = build_validator_agent(store=store)
    coach_agent = build_coach_agent(store=store)

    def load_profile(state: AppState, runtime: Runtime[AppContext]):
        assert runtime.store is not None

        doc = runtime.store.get(("users", runtime.context.user_id, "profile"), "current")
        if not doc:
            raise ValueError(
                f"No profile found in store for user_id={runtime.context.user_id}. "
                "Seed the user profile first."
            )

        profile = UserProfile.model_validate(doc.value)
        return {"user_profile": profile.model_dump()}

    def initialize_workflow_state(state: AppState, runtime: Runtime[AppContext]):
        return {
            "revision_count": 0,
            "max_revisions": 2,
            "approval_required": False,
            "approval_status": "pending",
            "risk_flags": [],
            "errors": [],
            "reviewer_feedback": [],
            "telemetry": {
                "user_id": runtime.context.user_id,
                "locale": runtime.context.locale,
                "unit_system": runtime.context.unit_system,
            },
        }

    def collect_missing_profile_fields(state: AppState, runtime: Runtime[AppContext]):
        profile = dict(state["user_profile"])
        questions: list[dict] = []

        if not profile.get("allergies"):
            questions.append(
                {
                    "field": "allergies",
                    "question": "Do you have any food allergies or intolerances? List them, or say 'none'.",
                    "type": "list_or_none",
                }
            )

        if "medications" not in profile or profile.get("medications") is None:
            questions.append(
                {
                    "field": "medications",
                    "question": "Are you taking any medications relevant to nutrition or supplements? List them, or say 'none'.",
                    "type": "list_or_none",
                }
            )

        if profile.get("budget_per_week") is None:
            questions.append(
                {
                    "field": "budget_per_week",
                    "question": "What is your weekly food budget?",
                    "type": "number",
                    "unit": "EUR",
                }
            )

        if not profile.get("meals_per_day"):
            questions.append(
                {
                    "field": "meals_per_day",
                    "question": "How many meals per day do you want?",
                    "type": "integer",
                }
            )

        if not questions:
            return {}

        answers = interrupt(
            {
                "type": "input_required",
                "reason": "missing_profile_fields",
                "message": "I need a few missing details before I can create a safe and accurate meal plan.",
                "questions": questions,
            }
        )

        profile.update(answers)

        assert runtime.store is not None
        runtime.store.put(
            ("users", runtime.context.user_id, "profile"),
            "current",
            profile,
        )

        return {"user_profile": profile}

    def load_memories(state: AppState, runtime: Runtime[AppContext]):
        assert runtime.store is not None

        prefs = runtime.store.search(
            ("users", runtime.context.user_id, "preferences"),
            limit=settings.default_memory_search_limit,
        )
        patterns = runtime.store.search(
            ("users", runtime.context.user_id, "patterns"),
            limit=settings.default_memory_search_limit,
        )

        memories = [doc.value for doc in prefs] + [doc.value for doc in patterns]
        return {"retrieved_memories": memories}

    def retrieve_domain_context(state: AppState, runtime: Runtime[AppContext]):
        assert runtime.store is not None

        docs = runtime.store.search(("domain", "guidelines"), limit=10)
        domain_context = [doc.value["text"] for doc in docs]
        return {"domain_context": domain_context}

    def compute_targets(state: AppState, runtime: Runtime[AppContext]):
        profile = UserProfile.model_validate(state["user_profile"])
        return {"macro_targets": compute_macro_targets(profile).model_dump()}

    def risk_gate(state: AppState, runtime: Runtime[AppContext]):
        profile = state["user_profile"]
        flags: list[str] = []

        medications = profile.get("medications", [])
        if medications and medications != ["none"]:
            flags.append("medication_present")

        if profile.get("medical_flags"):
            flags.append("medical_flags_present")

        return {
            "risk_flags": flags,
            "approval_required": len(flags) > 0,
            "approval_status": "pending" if flags else "approved",
        }

    def validator_node(state: AppState, runtime: Runtime[AppContext]):
        result = validator_agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": (
                            f"Validate this meal plan:\n{state['final_plan']}\n"
                            f"Risk flags: {state.get('risk_flags', [])}\n"
                            f"Reviewer feedback so far: {state.get('reviewer_feedback', [])}"
                        ),
                    }
                ]
            },
            context=runtime.context,
        )

        report = result["structured_response"]

        needs_review = (not report.approved) or bool(report.risk_flags)

        return {
            "risk_flags": report.risk_flags,
            "errors": report.issues,
            "approval_required": needs_review,
            "approval_status": "pending" if needs_review else "approved",
        }

    def human_review_node(state: AppState, runtime: Runtime[AppContext]):
        if not state.get("approval_required"):
            return {"approval_status": "approved"}

        decision = interrupt(
            {
                "type": "nutrition_plan_review",
                "user_id": runtime.context.user_id,
                "risk_flags": state.get("risk_flags", []),
                "plan": state["final_plan"],
                "errors": state.get("errors", []),
                "allowed_decisions": ["approved", "revise", "rejected"],
                "message": "Review the plan and either approve it, request revision, or reject it.",
            }
        )

        return {
            "approval_status": decision["status"],
            "reviewer_feedback": decision.get("feedback", []),
        }

    def revise_plan_node(state: AppState, runtime: Runtime[AppContext]):
        revision_count = state.get("revision_count", 0)
        feedback = state.get("reviewer_feedback", [])

        result = weekly_plan_subgraph.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": (
                            "Revise the current meal plan using the reviewer feedback.\n\n"
                            f"Current plan:\n{state['final_plan']}\n\n"
                            f"Reviewer feedback:\n{feedback}\n\n"
                            f"Macro targets:\n{state['macro_targets']}\n\n"
                            f"User profile:\n{state['user_profile']}\n\n"
                            f"Retrieved memories:\n{state.get('retrieved_memories', [])}\n\n"
                            f"Domain context:\n{state.get('domain_context', [])}"
                        ),
                    }
                ],
                "user_profile": state["user_profile"],
                "retrieved_memories": state.get("retrieved_memories", []),
                "domain_context": state.get("domain_context", []),
                "macro_targets": state["macro_targets"],
                "risk_flags": state.get("risk_flags", []),
            },
            context=runtime.context,
        )

        return {
            "final_plan": result["final_plan"],
            "revision_count": revision_count + 1,
            "approval_status": "pending",
            "errors": [],
        }

    def persist_plan(state: AppState, runtime: Runtime[AppContext]):
        assert runtime.store is not None
        ns = ("users", runtime.context.user_id, "plans")

        runtime.store.put(
            ns,
            str(uuid.uuid4()),
            {
                "plan": state["final_plan"],
                "risk_flags": state.get("risk_flags", []),
                "reviewer_feedback": state.get("reviewer_feedback", []),
                "revision_count": state.get("revision_count", 0),
            },
        )
        return {}

    def coach_node(state: AppState, runtime: Runtime[AppContext]):
        result = coach_agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": (
                            "Explain and coach this plan for adherence.\n\n"
                            f"Plan:\n{state['final_plan']}\n\n"
                            f"User goal: {state['user_profile'].get('goal')}\n"
                            f"Reviewer feedback: {state.get('reviewer_feedback', [])}"
                        ),
                    }
                ]
            },
            context=runtime.context,
        )

        coach = result["structured_response"].model_dump()

        final_plan = dict(state["final_plan"])
        final_plan["adherence_tips"] = coach["adherence_tips"]
        final_plan["coach_explanation"] = coach["explanation"]
        final_plan["prep_strategy"] = coach["prep_strategy"]

        return {"final_plan": final_plan}

    def route_after_validation(state: AppState):
        if state.get("approval_required"):
            return "human_review"
        return "persist"

    def route_after_review(state: AppState):
        status = state.get("approval_status", "pending")

        if status == "approved":
            return "persist"

        if status == "revise":
            if state.get("revision_count", 0) >= state.get("max_revisions", 2):
                return END
            return "revise_plan"

        return END

    builder = StateGraph(AppState, context_schema=AppContext)

    builder.add_node("load_profile", load_profile)
    builder.add_node("initialize_workflow_state", initialize_workflow_state)
    builder.add_node("collect_missing_profile_fields", collect_missing_profile_fields)
    builder.add_node("load_memories", load_memories)
    builder.add_node("retrieve_domain_context", retrieve_domain_context)
    builder.add_node("compute_targets", compute_targets)
    builder.add_node("risk_gate", risk_gate)
    builder.add_node("weekly_plan", weekly_plan_subgraph)
    builder.add_node("validator", validator_node)
    builder.add_node("human_review", human_review_node)
    builder.add_node("revise_plan", revise_plan_node)
    builder.add_node("persist", persist_plan)
    builder.add_node("coach", coach_node)

    builder.add_edge(START, "load_profile")
    builder.add_edge("load_profile", "initialize_workflow_state")
    builder.add_edge("initialize_workflow_state", "collect_missing_profile_fields")
    builder.add_edge("collect_missing_profile_fields", "load_memories")
    builder.add_edge("load_memories", "retrieve_domain_context")
    builder.add_edge("retrieve_domain_context", "compute_targets")
    builder.add_edge("compute_targets", "risk_gate")
    builder.add_edge("risk_gate", "weekly_plan")
    builder.add_edge("weekly_plan", "validator")

    builder.add_conditional_edges(
        "validator",
        route_after_validation,
        {
            "human_review": "human_review",
            "persist": "persist",
        },
    )

    builder.add_conditional_edges(
        "human_review",
        route_after_review,
        {
            "persist": "persist",
            "revise_plan": "revise_plan",
            END: END,
        },
    )

    builder.add_edge("revise_plan", "validator")
    builder.add_edge("persist", "coach")
    builder.add_edge("coach", END)

    return builder.compile(checkpointer=checkpointer, store=store)