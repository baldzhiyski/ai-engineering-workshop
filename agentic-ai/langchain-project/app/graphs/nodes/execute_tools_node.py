from ...tools.registry import ALL_TOOLS
from ...llms.models import get_general_model
from langchain.agents import create_agent
from ..state import WorkflowState
from langchain_core.messages import UserMessage,SystemMessage

def execute_tools_node(state: WorkflowState):
    if not state["plan"] or not state["plan"].needs_tools:
        return {"tool_results": []}

    agent = create_agent(
        model=get_general_model(),
        tools=ALL_TOOLS,
        system_prompt="Use tools only when required. Return concise intermediate findings."
    )

    result = agent.invoke({
        "messages": [
            SystemMessage(content="You are an agent that executes tools based on the user's plan."),
            UserMessage(content=f"User Input: {state['user_input']}\nPlan: {state['plan']}")
        ]
    })

    return {"tool_results": [str(result)]}