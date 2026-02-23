import json
from typing import TYPE_CHECKING
from .agent_response import AgentResponse
from .logging_utils import pretty_error, LogType, pretty_print

if TYPE_CHECKING:
    from ..core import BuildAgent

async def clean_response(response_text:str):
    # Extract JSON from response - handle cases where LLM adds extra text
        try:
            # Try to find JSON object in the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                pretty_error("JSON Extraction Failed", "No JSON object found in response", {"response": response_text[:200]})
                return None
                
            json_str = response_text[start_idx:end_idx]
            data = json.loads(json_str)
            return data
        except Exception as e:
            pretty_error("JSON Parsing Failed", str(e), {"response": response_text[:200]})
            return None
        
async def validate_response_schema(json_data: dict):
    # Re-create a clean model instance from the LLM payload
        try:
            agent_response = AgentResponse.model_validate(json_data, strict=True)
            return agent_response
        except Exception as e:
            pretty_error("Schema Validation Failed", str(e), {"data": json_data})
            return None
        
async def verify_response(response_text:str):
    # Full verification pipeline for LLM response
        json_data = await clean_response(response_text)
        if json_data is None:
            return "Response cleaning failed. Cannot proceed with invalid JSON."
        
        agent_response = await validate_response_schema(json_data)
        if agent_response is None:
            return f"Response validation failed for data: {json_data}"
        
        return agent_response
    
async def inject_context_and_reinvoke(agent:"BuildAgent", agent_response:AgentResponse, context:str):
    # Inject tool output and ask LLM to continue
    try:
        agent.messages.append({
            "role": "assistant", 
            "content": json.dumps(agent_response.model_dump()),
            "context": context
        })
        new_response = await agent.llm_client.invoke_model(messages=agent.messages)
        return new_response
    except Exception as e:
        pretty_error("Context Injection Error", str(e))
        return json.dumps({
            "text": f"Error injecting context: {e}",
            "tool_call": False,
            "task_complete": False,
            "error": str(e)
        })
    
async def handle_response_errors(agent:"BuildAgent", error_msg:str):
    # When LLM response parsing fails, ask it to correct the response
    try:
        agent.messages.append({
            "role": "system", 
            "content": f"Your previous response had an error: {error_msg}\n\nPlease respond again with valid JSON following the required format exactly."
        })
        new_response = await agent.llm_client.invoke_model(messages=agent.messages)
        return new_response
    except Exception as e:
        pretty_error("Error Handler Error", str(e))
        return json.dumps({
            "text": f"Error handling previous error: {e}",
            "tool_call": False,
            "task_complete": False,
            "error": str(e)
        })
    
    
        