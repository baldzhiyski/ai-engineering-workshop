# app/middleware/tool_monitoring.py
from typing import Callable
from langchain.agents.middleware import AgentMiddleware
from langchain.agents.middleware.types import ToolCallRequest, ToolMessage
from langgraph.types import Command

class NutritionToolMonitorMiddleware(AgentMiddleware):
    def wrap_tool_call(self, request: ToolCallRequest, handler: Callable):
        state = request.runtime.state
        tool_name = request.tool.name

        audit = state.get("audit_events", [])
        audit.append({"event": "tool_called", "tool": tool_name})

        if state.get("risk_level") == "high" and tool_name == "experimental_stack_builder":
            return Command(update={
                "audit_events": audit + [{"event": "tool_blocked", "tool": tool_name}],
                "messages": [ToolMessage(content="Tool blocked due to risk policy.", tool_call_id=request.tool_call["id"])],
            })

        try:
            result = handler(request)
            return Command(update={"audit_events": audit + [{"event": "tool_succeeded", "tool": tool_name}]})
        except Exception as e:
            return Command(update={
                "audit_events": audit + [{"event": "tool_failed", "tool": tool_name, "error": str(e)}],
                "messages": [ToolMessage(content=f"Tool failed safely: {e}", tool_call_id=request.tool_call["id"])],
            })