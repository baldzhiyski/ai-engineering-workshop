from ..llms.models import get_reasoning_model
from ..core.schemas.task_models import TaskPlan
from langchain.messages import SystemMessage, HumanMessage

PLANNER_SYSTEM_PROMPT = """
You are a planning agent.
Break the user request into an explicit execution plan.
Decide whether retrieval, SQL, or tools are needed.
Return structured output only.
"""


def build_task_plan(user_input: str) -> TaskPlan:
    model = get_reasoning_model()
    structured_model = model.with_structured_output(TaskPlan)
    return structured_model.invoke([
        SystemMessage(content=PLANNER_SYSTEM_PROMPT),
        HumanMessage(content=user_input),
    ])