# app/agents/coach.py
from __future__ import annotations
from pydantic import BaseModel, Field
from langchain.agents import create_agent
from ..config import settings

class CoachResponse(BaseModel):
    explanation: str
    adherence_tips: list[str] = Field(default_factory=list)
    prep_strategy: list[str] = Field(default_factory=list)

COACH_PROMPT = """
You are a high-performance nutrition coach.
Explain the plan clearly and practically.
Focus on compliance, prep simplicity, and habit strength.
No fake medical certainty.
"""

def build_coach_agent(*, store=None):
    return create_agent(
        model=settings.coach_model,
        tools=[],
        system_prompt=COACH_PROMPT,
        response_format=CoachResponse,
        store=store,
    )