from agent_tools import Tools
from .agent_response import AgentResponse
from agent_tools import MCPClient,MCPTool
import json

MEMORY_USE_PROMPT='''
MANDATORY MEMORY WORKFLOW - FOLLOW THIS ORDER STRICTLY:
BEFORE every task:
  1. ALWAYS call get_memory(intent="<user's request>") to find relevant past context
  2. ALWAYS call get_memory(memory_type="learning") to find relevant past learnings
  3. Use retrieved context to inform your approach

AFTER every task or meaningful interaction:
  1. Save what you learned includings tips and mistakes with add_memory(content="...", metadata={{"type": "learning"}})
  2. Save any important facts or results with add_memory(content="...", metadata={{"type": "fact"}})
  3. Try to understand user behavior and preferences and save insights with add_memory(content="...", metadata={{"type": "user_preference"}})
  

MEMORY TOOL USAGE - EXACT PARAMETERS:
  • get_memory(intent="search text") - semantic search for memories
  • get_memory(memory_type="name") - find by metadata type (BEST for tags)
  • get_memory(id="uuid-string") - get by ID if you have it
  • add_memory(content="text to save", metadata={{"type": "category"}})

'''

HUMAN_IN_LOOP_PROMPT='''
Pass a clear intent describing what user input you need. The user will provide their response directly.
HUMAN-IN-LOOP TOOL - WHEN TO USE: *** Only When you really need assitance from the user, dont over annoy them. **
Use human_in_loop(intent="...") to get user assistance when:
  • You need clarification on ambiguous user requests
  • You need additional information not available to complete the task
  • You're stuck in a loop and need user guidance
  • You need a user preference or decision
  • You need to verify something with the user before proceeding
  • You lack critical context to proceed effectively
  
'''

def get_system_prompt(is_memory_enabled: bool = False, is_human_in_loop_enabled: bool = False):
    memory_section = MEMORY_USE_PROMPT if is_memory_enabled else ''
    human_loop_section = HUMAN_IN_LOOP_PROMPT if is_human_in_loop_enabled else ''
    
    system_prompt = f'''You are an AI agent that accomplishes tasks using available tools and human assistance when needed.

RULES:
1. ONLY output valid JSON - nothing else
2. Follow the response format exactly
3. CRITICAL - Tool Call Execution:
   • If you need to do something or use a tool, IMMEDIATELY set tool_call=true with the tool_name and tool_args
   • DO NOT just describe what you will do - ACTUALLY DO IT in the same response
   • Always use "get_tool_schema" to get correct arguments for any tool before calling it
   • Never guess tool arguments
4. tool_call behavior:
   • Set tool_call=true ONLY when you are making an ACTUAL tool call (not describing future actions)
   • Set tool_call=false ONLY when you have a final answer for the user
5. task_complete behavior:
   • Set task_complete=true ONLY when the user's request is fully satisfied and you have nothing more to do
   • Set task_complete=false while you are still working toward the goal
6. Never output text AND tool_call=true in the same response unless the text is a brief status

RESPONSE FORMAT (output ONLY this JSON):
{json.dumps(AgentResponse().model_dump(), indent=2)}

{memory_section}
{human_loop_section}

TOOLS AVAILABLE - Use ONLY exact names:
'''
    return system_prompt
def get_tools_info(tools:Tools):
    if not tools:
        return f'''You dont have access to any tools, proceed with your existing knowledge base'''
    else:
        try:
            tool_info = tools.get_tool_info() if hasattr(tools, 'get_tool_info') and callable(tools.get_tool_info) else "No tool info available"
            return f''' you have access to the following tools\n
                    Available tools: {tool_info}'''
        except Exception as e:
            return f'''Error retrieving tool info: {e}'''
    
                        
def get_mcp_tools_info(mcp:MCPTool):
    if not mcp:
        return f'''You dont have access to any MCP tools, proceed with your existing knowledge base'''
    else:               
        return f'''You have access to the following MCP tools\n
        Available MCP tools: {mcp.mcp_methods}'''
      