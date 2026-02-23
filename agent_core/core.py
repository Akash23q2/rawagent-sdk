from agent_tools import Tools
import json
from .utils.prompts import get_system_prompt, get_tools_info
from .utils.tool_call import handle_tool_call, human_in_loop, get_tool_schema
from .utils.agent_response import AgentResponse
from .utils.process_response import verify_response, handle_response_errors, inject_context_and_reinvoke
from .utils import *
from .utils.logging_utils import pretty_print, pretty_error, LogType
from .memory import AgentMemory
from typing import List
from agent_tools.mcp_method import MCPClient, MCPTool
import asyncio
class BuildAgent:
    def __init__(self, name: str, description: str, llm_client, tools: Tools = None, mcp: MCPTool = None, enable_human_in_loop: bool = True, system_prompt: str = '', memory_collection_name: str = None):
        self.name = name
        self.description = description
        self.llm_client = llm_client
        self.tools = tools if tools else Tools()
        self.mcp = mcp
        self.consecutive_calls = 0
        # Configure the memory if enabled, and add the memory management functions as tools for the agent to use
        if memory_collection_name:
            AgentMemory(collection_name=memory_collection_name).register_memory_tools(self.tools)
        # Add human-in-loop tool if enabled
        if enable_human_in_loop:
            self.tools.add_tool(human_in_loop)
        # Build complete system message with tools information
        tools_info = get_tools_info(self.tools)
        system_content = f"{get_system_prompt(is_memory_enabled=memory_collection_name is not None, is_human_in_loop_enabled=enable_human_in_loop)}\n\n{tools_info}"
        self.messages = [{"role": "system", "content": system_content}]
        if self.mcp:
            self.messages.append({"role": "system", "content": f"New MCP tools added: {self.mcp.get_mcp_info()}. Update your knowledge base and tool access accordingly."})
        if system_prompt:
            self.messages.append({"role": "system", "content": system_prompt})  # add this system prompt too
        
    async def process_response(self, response_text: str, max_tries: int = 5):
        """Processes the response from the LLM, checks if a tool call is needed, and triggers the appropriate function if necessary."""
        # Extract JSON from response - handle cases where LLM adds extra text
        processed_response = await verify_response(response_text)
        if self.consecutive_calls > max_tries:
            pretty_error("Max Retries Exceeded", f"Maximum consecutive tool call attempts ({max_tries}) exceeded.", {"last_response": response_text})
            self.consecutive_calls = 0
            return f"Error: Maximum consecutive tool call attempts ({max_tries}) exceeded. Last response: {response_text}"
        
        if type(processed_response) == str:  # if response processing returns a string, it means there was an error in processing (either JSON parsing or schema validation), so we handle the error and ask the LLM to correct it by injecting the error message into the conversation
            self.consecutive_calls += 1
            pretty_error("Response Parsing Failed", processed_response, {"raw_response": response_text})
            new_response = await handle_response_errors(self, processed_response)
            return await self.process_response(new_response)
                    
        if not processed_response.tool_call:
            self.consecutive_calls = 0
            pretty_print(LogType.LLM_RESPONSE, "Agent Response", {"text": processed_response.text, "task_complete": processed_response.task_complete})
            
            # If task is not complete and no tool was called, ask LLM to continue working
            if not processed_response.task_complete:
                pretty_print(LogType.AGENT_INFO, "Task Incomplete", {"message": "Task not complete, requesting LLM to continue"})
                continue_prompt = "The task is not yet complete. Please continue working on it by calling the appropriate next tool."
                self.messages.append({"role": "user", "content": continue_prompt})
                new_response = await self.llm_client.invoke_model(messages=self.messages)
                return await self.process_response(new_response)
            
            return processed_response.text

        if processed_response.tool_call and self.consecutive_calls <= max_tries:
            pretty_print(LogType.TOOL_CALL, processed_response.tool_name, {"arguments": processed_response.tool_args})
            tool_output = await handle_tool_call(processed_response.tool_name, processed_response.tool_args, self.tools, self.mcp)
            
            # Check if tool execution succeeded or failed
            self.messages.append({"role": "user", "content": f"Tool '{processed_response.tool_name}' executed with output: {tool_output}"})
            new_response = await self.llm_client.invoke_model(messages=self.messages)
            return await self.process_response(new_response)
        else:
            pretty_error("Max Consecutive Calls", f"Maximum consecutive tool call attempts ({max_tries}) exceeded.", {"last_response": str(processed_response)})
            return f"Error: Maximum consecutive tool call attempts ({max_tries}) exceeded. Last error: {processed_response}"
                
    
    async def run_agent_async(self, query: str):
        try:
            self.messages.append({"role": "user", "content": query})
            response = await self.llm_client.invoke_model(messages=self.messages)
            
            if not response:
                pretty_error("LLM Response Empty", "Received empty response from LLM")
                return "Error: Empty response from LLM."
            
            processed_response = await self.process_response(response)
            
            # process_response always returns a string or AgentResponse
            if isinstance(processed_response, str):
                return processed_response
            
            # If it's an AgentResponse, return its text
            return processed_response.text if processed_response else "Error processing response from LLM."
        except Exception as e:
            pretty_error("Critical Agent Error", str(e))
            return f"Critical error: {str(e)}"
    
    def run_agent_sync(self, query: str):  # we want to loop until tool call none
        try:
            loop=asyncio.get_event_loop()
            return loop.run_until_complete(self.run_agent_async(query))
        except Exception as e:
            pretty_error("Critical Agent Error", str(e))
            return f"Critical error: {str(e)}"