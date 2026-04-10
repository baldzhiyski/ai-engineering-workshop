# app/middleware/tool_governance.py
from typing import Callable
from langchain.agents.middleware import AgentMiddleware, ModelRequest
from langchain.agents.middleware.types import ModelResponse

class NutritionToolGovernanceMiddleware(AgentMiddleware):
    def wrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        risk = request.state.get("risk_level", "low")
        role = getattr(request.runtime.context, "session_role", "user")

        tools = request.tools

        if role != "coach":
            tools = [t for t in tools if t.name not in {"persist_clinician_note"}]

        if risk == "high":
            blocked = {"unsafe_supplement_lookup", "experimental_stack_builder"}
            tools = [t for t in tools if t.name not in blocked]

        request = request.override(tools=tools)
        return handler(request)