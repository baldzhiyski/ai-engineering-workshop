from pydantic import BaseModel,Field
from typing import Optional,List,Literal

class ExecutionStep(BaseModel):
    step_number: int
    description: str
    tool_name: Optional[str] = None
    expected_output: Optional[str] = None

class TaskPlan(BaseModel):
    task_type: Literal[
        "chat",
        "retrieval_qa",
        "document_analysis",
        "sql_analysis",
        "research",
        "multi_step_workflow"
    ]
    objective: str
    needs_retrieval: bool
    needs_sql: bool
    needs_tools: bool
    steps: List[ExecutionStep]

class CritiqueReport(BaseModel):
    grounded: bool
    complete: bool
    confidence: float = Field(ge=0.0, le=1.0)
    issues: List[str]
    revision_needed: bool