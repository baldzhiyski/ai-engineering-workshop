from langgraph.graph import StateGraph, START, END
from ..graphs.state import WorkflowState
from ..graphs.nodes.plan_node import plan_node
from ..graphs.nodes.retrieve_node import retrieve_node
from ..graphs.nodes.tool_node import execute_tools_node
from ..graphs.nodes.syntesis_node import synthesize_node
from ..graphs.nodes.critique_node import critique_node
from ..graphs.nodes.revise_node import revise_node


def after_critique(state: WorkflowState):
    critique = state.get("critique")
    if critique and critique.revision_needed and state.get("retries", 0) < 1:
        return "revise"
    return "end"


def build_workflow_graph():
    graph = StateGraph(WorkflowState)

    graph.add_node("plan", plan_node)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("tools", execute_tools_node)
    graph.add_node("synthesize", synthesize_node)
    graph.add_node("critique", critique_node)
    graph.add_node("revise", revise_node)

    graph.add_edge(START, "plan")
    graph.add_edge("plan", "retrieve")
    graph.add_edge("retrieve", "tools")
    graph.add_edge("tools", "synthesize")
    graph.add_edge("synthesize", "critique")

    graph.add_conditional_edges(
        "critique",
        after_critique,
        {
            "revise": "revise",
            "end": END,
        }
    )

    graph.add_edge("revise", END)

    return graph.compile()