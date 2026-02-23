from agent_tools import Tools,MCPClient,MCPTool
import json
import asyncio
from .agent_response import AgentResponse
from .logging_utils import pretty_error, pretty_print, LogType

async def human_in_loop(intent: str) -> str:
    '''Use this tool when you need additional user assistance, extra information, user preferences, or clarification.
    
    Use this tool when:
    - You need clarification on ambiguous requests
    - You need information not available in your knowledge
    - You're stuck in a loop and need guidance
    - You need a user decision or preference
    - You need to verify something before proceeding
    
    Args:
        intent: A clear description of what user input/assistance you need
    
    Returns:
        The user's response/input
    '''
    pretty_print(LogType.HUMAN_IN_LOOP, title=intent)
    response = input('Enter your response: ')
    return response

async def get_tool_schema(tool_name: str, tools: Tools, mcp: MCPTool):
    '''Fetch the schema for a given tool from either the local tools registry or the MCP client.'''
    if tool_name in tools._tools:
        schema= tools._tool_method_schema[tool_name].model_json_schema()
        return schema
    elif mcp and tool_name in mcp.mcp_methods:
        return mcp.mcp_method_schema[tool_name].model_json_schema() or mcp.mcp_method_schema[tool_name]
    else:
        return f"Error: Tool '{tool_name}' not found in either local tools or MCP client."

async def make_tool_call(tool_name: str, tool_args: dict, tools: Tools):
    '''Make a tool call by invoking the corresponding function from the tools registry.'''
    if tool_name not in tools._tools: 
        error_msg = f"Tool '{tool_name}' not found."
        pretty_error("Tool Not Found", error_msg, {"available_tools": list(tools._tools.keys())})
        return {"status": "error", "error": error_msg, "tool": tool_name}
    if tool_name in tools._tools:
        tool_func = tools._tool_method[tool_name]
        if isinstance(tool_args, dict):
            try:
                output=tool_func(**tool_args)
                # Wrap successful execution
                return {"status": "success", "output": output, "tool": tool_name, "args": tool_args}
            except Exception as e:
                error_msg = f"Error executing tool '{tool_name}' with arguments {tool_args}: {e}"
                pretty_error("Tool Execution Failed", str(e), {"tool": tool_name, "arguments": tool_args})
                return {"status": "error", "error": error_msg, "tool": tool_name, "args": tool_args}
        else:
            error_msg = f"Error: Tool arguments for '{tool_name}' must be a dictionary as per method schema."
            pretty_error("Invalid Tool Arguments", "Arguments must be a dictionary", {"tool": tool_name, "received": type(tool_args).__name__})
            return {"status": "error", "error": error_msg, "tool": tool_name}
    
async def make_mcp_tool_call(tool_name: str, tool_args: dict, mcp: MCPTool):
    '''Make a tool call to an MCP method by invoking the corresponding function from the MCP client.'''
    if not mcp or tool_name not in mcp.mcp_methods:
        error_msg = f"Error: MCP Tool '{tool_name}' not found or MCP client not configured."
        pretty_error("MCP Tool Not Found", error_msg, {"mcp_available": mcp is not None})
        return {"status": "error", "error": error_msg, "tool": tool_name}
    if mcp and tool_name in mcp.mcp_methods:
        if isinstance(tool_args, dict):
            try:
                session = await mcp.get_session(tool_name)
                if not session:
                    error_msg = f"Error: No active session found for MCP Tool '{tool_name}'."
                    pretty_error("MCP Session Error", error_msg, {"tool": tool_name})
                    return {"status": "error", "error": error_msg, "tool": tool_name}
                result = await session.call_tool(tool_name, tool_args)
                return {"status": "success", "output": result, "tool": tool_name, "args": tool_args}
            except Exception as e:
                error_msg = f"Error executing MCP tool '{tool_name}' with arguments {tool_args}: {e}"
                pretty_error("MCP Tool Execution Failed", str(e), {"tool": tool_name, "arguments": tool_args})
                return {"status": "error", "error": error_msg, "tool": tool_name, "args": tool_args}
        else:
            error_msg = f"Error: MCP Tool arguments for '{tool_name}' must be a dictionary as per method schema."
            pretty_error("Invalid MCP Arguments", "Arguments must be a dictionary", {"tool": tool_name, "received": type(tool_args).__name__})
            return {"status": "error", "error": error_msg, "tool": tool_name}


async def handle_tool_call(tool_name: str, tool_args: dict, tools: Tools=None, mcp: MCPTool=None):
    '''Handle the execution of a tool call based on the tool name and arguments.'''
    try:
        # Handle human-in-loop tool
        if tool_name == 'human_in_loop':
            intent = tool_args.get('intent', 'Awaiting user input')
            user_response = await human_in_loop(intent)
            pretty_print(LogType.TOOL_RESPONSE, "Human Input Received", {"intent": intent, "response": user_response})
            return {"status": "success", "output": user_response, "tool": tool_name, "args": tool_args}
        
        elif tool_name == 'get_tool_schema': 
            return await get_tool_schema(tool_name, tools, mcp)
        
        elif tools and mcp and tool_name not in tools._tools and tool_name not in mcp.mcp_methods:
            error_msg = f"Error: Tool '{tool_name}' not found."
            pretty_error("Tool Not Found", error_msg, {"local_tools": list(tools._tools.keys()), "mcp_tools": list(mcp.mcp_methods) if mcp else []})
            return {"status": "error", "error": error_msg}
        
        elif tools and tool_name in tools._tools:
            return await make_tool_call(tool_name, tool_args, tools)
        
        elif mcp and tool_name in mcp.mcp_methods:
            return await make_mcp_tool_call(tool_name, tool_args, mcp)
        else:
            error_msg = f"Error: Tool '{tool_name}' not found."
            pretty_error("Tool Not Found", error_msg)
            return {"status": "error", "error": error_msg}

    except Exception as e:
        error_msg = f"Error executing tool '{tool_name}': {e}"
        pretty_error("Tool Execution Error", str(e), {"tool": tool_name})
        return {"status": "error", "error": error_msg}
    

