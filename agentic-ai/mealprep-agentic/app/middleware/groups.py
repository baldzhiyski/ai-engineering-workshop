# app/agents/middleware_profiles.py
from langchain.agents.middleware import (
    PIIMiddleware,
    ModelCallLimitMiddleware,
    ToolCallLimitMiddleware,
    ModelFallbackMiddleware,
    HumanInTheLoopMiddleware,
    SummarizationMiddleware,
)

from ..middleware.input_policy import classify_request_risk
from ..middleware.prompt_hardening import add_risk_specific_instructions
from ..middleware.model_router import NutritionModelRouter
from ..middleware.tool_governence import NutritionToolGovernanceMiddleware
from ..middleware.output_guardrails import validate_latest_ai_output
from ..middleware.post_run import finalize_audit
from ..middleware.tool_monitoring import NutritionToolMonitorMiddleware
from ..config import settings


def planner_middleware():
    return [
        PIIMiddleware("email", strategy="redact", apply_to_input=True, apply_to_output=True),
        classify_request_risk,
        ModelCallLimitMiddleware(run_limit=8, thread_limit=30, exit_behavior="end"),
        ToolCallLimitMiddleware(run_limit=12, thread_limit=40),
        ToolCallLimitMiddleware(tool_name="search_recipe_corpus", run_limit=4, thread_limit=12),
        add_risk_specific_instructions,
        NutritionModelRouter(),
        NutritionToolGovernanceMiddleware(),
        SummarizationMiddleware(
            model=settings.fast_model,
            trigger=("tokens", 5000),
            keep=("messages", 10),
        ),
        ModelFallbackMiddleware(settings.default_model, settings.additional_models),

        NutritionToolMonitorMiddleware(),
        validate_latest_ai_output,
        finalize_audit,
    ]


def validator_middleware():
    return [
        ModelFallbackMiddleware(settings.validator_model, settings.default_model),
    ]


def coach_middleware():
    return [
        PIIMiddleware("email", strategy="redact", apply_to_input=True, apply_to_output=True),
        ModelFallbackMiddleware(settings.coach_model, settings.default_model),
    ]