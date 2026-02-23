from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class AgentResponse(BaseModel):
    '''Defines the structure of the agent's response.'''
    text: Optional[str] = Field(
        default=None,
        description="Response text for the user. Use when no tool is needed or after tools complete."
    )
    task_execution_plan: Optional[str] = Field(
        default=None,
        description="Optional: Brief execution plan if needed."
    )
    tool_call: bool = Field(
        default=False,
        description="true = calling a tool, false = ready to respond to user"
    )
    tool_name: Optional[str] = Field(
        default=None,
        description="Name of the tool to call (must match available tools exactly)"
    )
    tool_args: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Arguments dictionary for the tool call"
    )
    task_complete: bool = Field(
        default=False,
        description="true when task fully completed, false while working"
    )
    last_called_tool: Optional[str] = Field(
        default=None,
        description="Name of the last tool that was successfully executed"
    )
    current_task: Optional[str] = Field(
        default=None,
        description="Brief description of the current task being executed"
    )
    next_tool_to_call: Optional[str] = Field(
        default=None,
        description="Optional: name of the next tool to call if known"
    )
    consecutive_tool_calls: int = Field(
        default=0,
        description="Counter for consecutive tool calls (for debugging)"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if something went wrong, null otherwise"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": None,
                "task_execution_plan": None,
                "tool_call": True,
                "tool_name": "web_search",
                "tool_args": {"url": "https://example.com"},
                "task_complete": False,
                "last_called_tool": None,
                "current_task": "Executing web search",
                "next_tool_to_call": None,
                "consecutive_tool_calls": 0,
                "error": None
            }
        }