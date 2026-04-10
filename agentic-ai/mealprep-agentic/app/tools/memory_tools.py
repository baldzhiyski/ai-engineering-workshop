# app/tools/memory_tools.py
from __future__ import annotations
import uuid
from langchain.tools import tool, ToolRuntime
from ..context import AppContext

@tool
def get_user_preferences(runtime: ToolRuntime[AppContext]) -> dict:
    """Load long-term user preferences and prior plan patterns."""
    assert runtime.store is not None
    namespace = ("users", runtime.context.user_id, "preferences")
    docs = runtime.store.search(namespace, limit=10)
    return [doc.value for doc in docs]

@tool
def remember_user_fact(key: str, value: str, runtime: ToolRuntime[AppContext]) -> str:
    """Persist a durable preference or fact across sessions."""
    assert runtime.store is not None
    namespace = ("users", runtime.context.user_id, "preferences")
    runtime.store.put(namespace, key, {"key": key, "value": value})
    return f"Stored memory '{key}'"