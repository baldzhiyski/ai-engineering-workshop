from ...llms.models import get_general_model
from ..state import WorkflowState
from langchain.messages import SystemMessage, HumanMessage

REVISION_PROMPT = """
Revise the draft using the critique.
Fix the listed issues and keep the answer grounded.
"""


def revise_node(state: WorkflowState):
    if not state.critique or not state.critique.revision_needed:
        return {"final_answer": state.draft_answer}

    model = get_general_model()
    result = model.invoke([
        SystemMessage(content=REVISION_PROMPT),
        HumanMessage(content=f"User Input: {state.user_input}\nPlan: {state.plan}\nRetrieved Context: {state.retrieved_context}\nTool Results: {state.tool_results}\nDraft Answer: {state.draft_answer}\nCritique: {state.critique}"),
    ])
    return {"final_answer": result.content}