# agent_core

Core orchestration for agents: conversation state, LLM prompting, tool invocation, human-in-the-loop, semantic memory, and structured responses.

## BuildAgent
Location: `agent_core/core.py`

### Purpose
Coordinates the end-to-end loop with the model and tools:
- Builds system prompts with available tools and optional memory/human-in-loop guidance
- Ensures the LLM returns JSON conforming to `AgentResponse`
- Detects tool calls and dispatches them
- Injects tool results back to the LLM and retries as needed

### Initialization
```python
BuildAgent(
  name: str,
  description: str,
  llm_client,                         
  tools: agent_tools.Tools | None = None,
  mcp: agent_tools.MCPTool | None = None,
  enable_human_in_loop: bool = True,
  system_prompt: str = "",
  memory_collection_name: str | None = None,
)
```
- When `memory_collection_name` is provided, memory tools are auto-registered to the agent
- When `enable_human_in_loop` is true, a `human_in_loop(intent: str)` tool is added

### Methods
- `async process_response(response_text: str, max_tries: int = 5)` — Internal loop to validate responses and execute tools
- `async run_agent_async(query: str) -> str` — Runs agent for the given query
- `run_agent_sync(query: str) -> str` — Synchronous wrapper around `run_agent_async`

### Message contract
`BuildAgent` expects the model to emit JSON matching `AgentResponse` (see below). It composes a system message that includes:
- Rules enforcing JSON-only output
- Tool usage guidance (including `get_tool_schema` hinting)
- Memory/human-in-loop sections when enabled

## AgentResponse (schema)
Location: `agent_core/utils/agent_response.py`

A Pydantic model that defines the LLM response contract:
- `text: str | None` — Final user-facing text (set only when not calling a tool)
- `task_execution_plan: str | None` — Optional brief plan
- `tool_call: bool` — True when actually calling a tool in this response
- `tool_name: str | None` — Exact tool name
- `tool_args: dict | None` — Arguments dict for the tool
- `task_complete: bool` — True when the task is fully done
- `last_called_tool: str | None`
- `current_task: str | None`
- `next_tool_to_call: str | None`
- `consecutive_tool_calls: int` — Debugging counter
- `error: str | None`

This schema is embedded into the system prompt so the model can mirror it.

## Memory: AgentMemory
Location: `agent_core/memory.py`

Backed by ChromaDB (persistent at `./chroma_db`).

### Methods
- `add_memory(content: str, metadata: dict | None = None) -> str`
  - Returns generated memory ID
  - Example metadata: `{ "type": "learning" | "fact" | "user_preference" }`
- `get_memory(intent: str | None = None, id: str | None = None, memory_type: str | None = None)`
  - `id` — fetch by exact ID
  - `memory_type` — manual filter over stored metadata
  - `intent` — semantic search via `query_texts`
  - Returns a dict/list on success or a string error message
- `delete_memory(id: str) -> str`
- `list_all_memories() -> list | str`
- `register_memory_tools(tools: agent_tools.Tools)` — Registers `add_memory`, `get_memory`, and `delete_memory` as callable tools

## Response processing utilities
Location: `agent_core/utils/process_response.py`

- `clean_response(response_text: str)` — Extract JSON from free-form model output
- `validate_response_schema(json_data: dict)` — Validate against `AgentResponse`
- `verify_response(response_text: str)` — Full pipeline; returns `AgentResponse` or an error string
- `inject_context_and_reinvoke(agent, agent_response, context)` — Inject tool output and re-query the LLM
- `handle_response_errors(agent, error_msg)` — Ask the LLM to correct invalid responses

## Prompt utilities
Location: `agent_core/utils/prompts.py`

- `get_system_prompt(is_memory_enabled: bool, is_human_in_loop_enabled: bool) -> str` — Base system prompt with rules and embedded schema
- `get_tools_info(tools: agent_tools.Tools) -> str` — Lists available tools for the prompt
- `get_mcp_tools_info(mcp: agent_tools.MCPTool) -> str` — Lists MCP methods for the prompt

## Tool calling utilities
Location: `agent_core/utils/tool_call.py`

- `human_in_loop(intent: str) -> str` — Interactive prompt via stdin; intended for disambiguation or user approvals
- `get_tool_schema(tool_name: str, tools: Tools, mcp: MCPTool)` — Returns JSON schema for local or MCP tools
- `handle_tool_call(tool_name: str, tool_args: dict, tools: Tools | None, mcp: MCPTool | None)` — Routes to local tools or MCP tools and standardizes output

Note: Local tools are executed directly from the `Tools` registry. MCP tools are called via an active MCP session.

## Logging utilities
Location: `agent_core/utils/logging_utils.py`

- `pretty_print(LogType, title: str = "", content: Any = None)` — Categorized, colored logging
- `pretty_error(title: str, error_msg: str, context: Any = None)` — Error formatting
- `section_header(title: str, emoji: str = "━")` — Visual sectioning
- `LogType` and `Colors` enums for styling
