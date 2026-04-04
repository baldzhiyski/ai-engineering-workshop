from typing import List, Optional, Dict, Literal
from pydantic import BaseModel, Field

from ..core.schemas.task_models import TaskPlan, CritiqueReport


class MessageState(BaseModel):
    role: Literal["user", "assistant", "tool", "system"]
    content: str


class WorkflowState(BaseModel):
    messages: List[MessageState] = Field(default_factory=list)
    user_input: str
    plan: Optional[TaskPlan] = None
    retrieved_context: str = ""
    tool_results: List[str] = Field(default_factory=list)
    draft_answer: str = ""
    critique: Optional[CritiqueReport] = None
    final_answer: str = ""
    retries: int = 0


def build_initial_state(
    user_input: str,
    messages: List[Dict[str, str]],
) -> WorkflowState:
    return WorkflowState(
        user_input=user_input,
        messages=[MessageState(**msg) for msg in messages],
    )