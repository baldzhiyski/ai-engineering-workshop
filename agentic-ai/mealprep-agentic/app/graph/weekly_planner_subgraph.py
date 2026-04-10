# app/graph/weekly_plan_subgraph.py
from __future__ import annotations

from langgraph.graph import StateGraph, START, END
from langgraph.runtime import Runtime
from ..context import AppContext
from ..state import AppState
from ..agents.planner import build_planner_agent

def build_weekly_plan_subgraph(*, store=None, checkpointer=None):
    planner_agent = build_planner_agent(store=store, checkpointer=checkpointer)

    def planner_node(state: AppState, runtime: Runtime[AppContext]):
        prompt = f"""
        Build a 7-day meal plan.

        User profile:
        {state['user_profile']}

        Retrieved memories:
        {state.get('retrieved_memories', [])}

        Domain context:
        {state.get('domain_context', [])}

        Macro targets:
        {state['macro_targets']}

        User request:
        {state['messages'][-1].content}
        """
        result = planner_agent.invoke(
            {"messages": [{"role": "user", "content": prompt}]},
            context=runtime.context,
        )
        plan = result["structured_response"]
        return {"final_plan": plan.model_dump()}

    builder = StateGraph(AppState, context_schema=AppContext)
    builder.add_node("planner_node", planner_node)
    builder.add_edge(START, "planner_node")
    builder.add_edge("planner_node", END)
    return builder.compile()