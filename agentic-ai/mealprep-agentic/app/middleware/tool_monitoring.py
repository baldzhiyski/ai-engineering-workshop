from typing import Callable
from langchain.agents.middleware import AgentMiddleware
from langchain.agents.middleware.types import ToolCallRequest, ToolMessage
from langgraph.types import Command
class NutritionToolMonitorMiddleware(AgentMiddleware):
    def wrap_tool_call(self, request: ToolCallRequest, handler: Callable):
        state = request.runtime.state
        tool_name = request.tool.name

        # Block specific risky tools up front if needed
        if state.get("risk_level") == "high" and tool_name == "experimental_stack_builder":
            return ToolMessage(
                content="Tool blocked due to risk policy.",
                tool_call_id=request.tool_call["id"],
            )

        try:
            # IMPORTANT: preserve the real tool response message/result
            result = handler(request)
            return result
        except Exception as e:
            # On failure, return a ToolMessage tied to the same tool_call_id
            return ToolMessage(
                content=f"Tool failed safely: {e}",
                tool_call_id=request.tool_call["id"],
            )