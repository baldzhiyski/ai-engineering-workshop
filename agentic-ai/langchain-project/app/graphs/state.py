from typing_extensions import TypedDict, Annotated
from typing import List, Optional
import operator
from ..core.schemas.task_models import TaskPlan, CritiqueReport

class WorkflowState(TypedDict):
    messages: Annotated[List[dict], operator.add]
    user_input: str
    plan: Optional[TaskPlan]
    retrieved_context: str
    tool_results: List[str]
    draft_answer: str
    critique: Optional[CritiqueReport]
    final_answer: str
    retries: int