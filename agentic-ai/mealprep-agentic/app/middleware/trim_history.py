# app/middleware/trim_history.py
from __future__ import annotations
from typing import Any
from langchain.agents import AgentState
from langchain.agents.middleware import before_model, SummarizationMiddleware
from langchain.messages import RemoveMessage
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langgraph.runtime import Runtime

@before_model
def trim_message_history(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    messages = state["messages"]
    if len(messages) <= 8:
        return None

    first_msg = messages[0]
    recent = messages[-7:]
    return {
        "messages": [
            RemoveMessage(id=REMOVE_ALL_MESSAGES),
            first_msg,
            *recent,
        ]
    }

summarizer = SummarizationMiddleware(
    model="openai:gpt-4.1-mini",
    max_tokens_before_summary=8000,
    keep_last_n_messages=8,
)