# app/middleware/model_router.py
from dataclasses import dataclass
from typing import Callable
from langchain.agents.middleware import AgentMiddleware, ModelRequest
from langchain.agents.middleware.types import ModelResponse
from ..config import settings

@dataclass
class ModelTierConfig:
    fast_model: str = settings.fast_model
    strong_model: str = settings.default_model

class NutritionModelRouter(AgentMiddleware):
    def __init__(self, cfg: ModelTierConfig | None = None):
        super().__init__()
        self.cfg = cfg or ModelTierConfig()

    def wrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        risk = request.state.get("risk_level", "low")
        msg_count = len(request.state["messages"])

        chosen = self.cfg.fast_model
        if risk == "high" or msg_count > 12:
            chosen = self.cfg.strong_model

        request = request.override(model=chosen)
        return handler(request)