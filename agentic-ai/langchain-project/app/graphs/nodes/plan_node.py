from ...agents.planner_agent import build_task_plan
from ..state import WorkflowState

def plan_node(state: WorkflowState):
    plan = build_task_plan(state.user_input)
    return {"plan": plan}