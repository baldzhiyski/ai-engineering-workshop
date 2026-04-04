from langgraph.graph import StateGraph, START, END
from ..graphs.state import WorkflowState
from ..graphs.nodes.plan_node import plan_node
from ..graphs.nodes.retrieve_node import retrieve_node
from ..graphs.nodes.tool_node import execute_tools_node
from ..graphs.nodes.syntesis_node import synthesize_node
from ..graphs.nodes.critique_node import critique_node
from ..graphs.nodes.revise_node import revise_node
import logging

logger = logging.getLogger(__name__)


def after_critique(state: WorkflowState):
    # Always proceed to the revise node. The revise node will copy the
    # draft_answer into final_answer when no revision is requested by the
    # critic, and will perform a revision when needed. This ensures that
    # a `final_answer` field is present in the terminal state.
    return "revise"


def _make_logging_node(name: str, fn):
    """Return a wrapper around node `fn` which logs entry, exit, and errors.

    The wrapper logs a compact snapshot of the state's key fields so the
    log stream shows which nodes ran and what they returned.
    """

    def wrapper(state: WorkflowState):
        try:
            logger.info("GRAPH NODE START [%s] user_input=%s plan=%s", name, getattr(state, "user_input", None), getattr(state, "plan", None))
            result = fn(state)
            logger.info("GRAPH NODE END   [%s] result=%s", name, result)
            return result
        except Exception:
            logger.exception("GRAPH NODE ERROR [%s]", name)
            raise

    return wrapper


def build_workflow_graph():
    graph = StateGraph(WorkflowState)

    # Wrap each node with logging to make execution visible in the logs
    graph.add_node("plan", _make_logging_node("plan", plan_node))
    graph.add_node("retrieve", _make_logging_node("retrieve", retrieve_node))
    graph.add_node("tools", _make_logging_node("tools", execute_tools_node))
    graph.add_node("synthesize", _make_logging_node("synthesize", synthesize_node))
    graph.add_node("critique", _make_logging_node("critique", critique_node))
    graph.add_node("revise", _make_logging_node("revise", revise_node))

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