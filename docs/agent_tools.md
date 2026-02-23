# agent_tools

Tools registry for local Python callables and wrappers for MCP-based external tool servers.

## Tools (local registry)
Location: `agent_tools/tools_method.py`

### Overview
`Tools` registers Python callables as agent tools and automatically derives a JSON schema for arguments from function type hints using Pydantic.

### API
- `add_tool(method: Callable)`
  - All parameters must have type annotations
  - Docstring becomes the tool description
  - Returns the original method, so it remains usable directly
- `get_tools() -> dict[str, str]` — Mapping of tool name to description
- `get_tool_info() -> list[tuple[str, str]]` — Readable list of tools
- `get_tool_method_schema(method_name: str) -> pydantic.BaseModel` — Pydantic model describing the tool’s args

### Example
```python
from agent_tools import Tools

def add(a: int, b: int) -> int:
    """Add two integers and return the sum."""
    return a + b

# Register the tool
tools = Tools()
tools.add_tool(add)

# Introspection
print(tools.get_tool_info())              # [('add', 'Add two integers and return the sum.')]
SchemaModel = tools.get_tool_method_schema('add')
print(SchemaModel.model_json_schema())    # JSON schema usable by an LLM
```

## MCP (Model Context Protocol) integration
Locations: `agent_tools/mcp_method.py`

### MCPClient
Connects to an MCP stdio server (Python `.py` or Node `.js`).

- `MCPClient(server_script_path: str)`
  - Infers command: `python` for `.py`, `node` for `.js`
- `await connect()` — Starts stdio client, initializes session, discovers tools
  - Discovers tool names, descriptions, and input schemas
- `await disconnect()` — Closes session and resources
- `await call_tool(tool_name: str, tool_args: dict)` — Calls a remote MCP tool by name

### MCPTool
Aggregates one or more MCP clients and exposes their tool metadata for the agent.

- `await add_mcp_client(mcp_client_path: str)` — Connects and merges discovered tools
- `await remove_mcp_client(mcp_client_path: str)` — Disconnects and removes tools from the registry
- `async get_session(tool_name: str)` — Returns the active session to call a particular tool
- `get_mcp_info() -> list[tuple[str, str]]` — Returns discovered MCP tools (name, description)

### Usage sketch
```python
import asyncio
from agent_tools import MCPTool

async def main():
    mcp = MCPTool()
    # Path to a running MCP server script that supports stdio
    await mcp.add_mcp_client("path/to/server.py")
    # Later: BuildAgent(..., mcp=mcp)

asyncio.run(main())
```

### In-agent behavior
When an LLM response contains a `tool_call` with a name matching an MCP tool, the agent routes the call to an MCP session and returns standardized output to the LLM for the next step.
