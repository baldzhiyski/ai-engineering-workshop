# app/middleware/risk_guardrails.py
from __future__ import annotations
from typing import Callable
from langchain.agents.middleware import AgentMiddleware, ModelRequest, ModelResponse

class NutritionRiskMiddleware(AgentMiddleware):
    """Conservative blocker for unsafe medical-style advice."""

    def wrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        last_user = ""
        for msg in reversed(request.state["messages"]):
            if getattr(msg, "type", None) == "human":
                last_user = str(msg.content).lower()
                break

        risky_terms = ["diagnose", "prescribe", "replace medication", "cure", "treat disease"]
        if any(term in last_user for term in risky_terms):
            raise ValueError("Medical-diagnosis or prescription request blocked.")
        return handler(request)