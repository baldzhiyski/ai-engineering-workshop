from ...llms.models import get_general_model
from ...core.schemas.task_models import CritiqueReport
from ...graphs.state import WorkflowState
from langchain.messages import SystemMessage, HumanMessage


CRITIC_PROMPT = """
You are a critic agent.
Check if the draft is grounded, complete, and logically consistent.
Return structured output only.
"""


def critique_node(state: WorkflowState):
    model = get_general_model()
    structured_model = model.with_structured_output(CritiqueReport)
    critique = structured_model.invoke([
        SystemMessage(content=CRITIC_PROMPT),
        HumanMessage(content=f"User Input: {state.user_input}\nPlan: {state.plan}\nRetrieved Context: {state.retrieved_context}\nTool Results: {state.tool_results}\nDraft Answer: {state.draft_answer}"),
    ])
    return {"critique": critique}