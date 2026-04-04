from ...llms.models import get_general_model
from ..state import WorkflowState
from langchain_core.messages import HumanMessage, SystemMessage

SYNTHESIS_PROMPT = """
You are a synthesis agent.
Use the task plan, retrieved context, and tool results.
Produce a grounded, clear, final draft.
If evidence is weak, say so.
"""


def synthesize_node(state: WorkflowState):
    model = get_general_model()
    content = f"""
Plan:
{state.plan}\n

Retrieved context:
{state.retrieved_context}

Tool results:
{state.tool_results} = model.invoke([
"""
    result = model.invoke([
        SystemMessage(content=SYNTHESIS_PROMPT),
        HumanMessage(content=content)
    ])
    return {"draft_answer": result.content}