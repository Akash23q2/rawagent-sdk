# rawagent-sdk

A lightweight, agentic AI framework for Python focused on tool-use, structured LLM responses, human-in-the-loop workflows, semantic memory (ChromaDB), and optional MCP tool integration.

## Features
- BuildAgent orchestrates conversations, tool calling, retries, and error handling
- Pydantic schema (AgentResponse) to enforce JSON-only LLM outputs
- Tool registry (Tools) with automatic argument schema from function signatures
- Human-in-the-loop utility for interactive clarification and decisions
- Semantic memory via ChromaDB (add, query, delete, list)
- MCP client wrapper for stdio-based external tool servers
- Pretty logging for tool/LLM/memory events

## Install dependencies
If packaging isn’t configured yet, install direct dependencies:

```bash
pip install -U chromadb mcp openai pydantic pyttsx3 python-dotenv
```

Or, if you have a working build backend configured, you can try:

```bash
pip install -e .
```

## Quickstart
```python
from agent_core import BuildAgent
from agent_tools import Tools
from llm_model.OpenAi import OpenAi

# 1) Define a simple tool
from typing import List

def search_docs(query: str, top_k: int = 3) -> List[str]:
    """Search internal docs for a query and return top_k snippets."""
    corpus = [
        "RawAgent SDK lets you build agentic workflows.",
        "Tools are registered from Python callables with type hints.",
        "ChromaDB powers semantic memory for the agent.",
    ]
    return [t for t in corpus if query.lower() in t.lower()][:top_k]

# 2) Register tools
tools = Tools()
tools.add_tool(search_docs)

# 3) LLM client (read your key from env or secret manager)
import os
llm = OpenAi(api_key=os.environ.get("OPENAI_API_KEY", ""))

# 4) Build the agent (enable memory tools by passing a collection name)
agent = BuildAgent(
    name="RawAgent",
    description="General-purpose agent with tools and memory",
    llm_client=llm,
    tools=tools,
    enable_human_in_loop=True,
    memory_collection_name="demo_memory",
)

# 5) Run synchronously
result = agent.run_agent_sync("Find references about tools and memory")
print(result)
```

## Components
- docs/agent_core.md – BuildAgent, AgentMemory, utils (responses, prompts, logging, response processing)
- docs/agent_tools.md – Tools registry, MCPClient/MCPTool integration
- docs/llm_model.md – OpenAi client wrapper and message contract

## Notes
- The agent expects the model to output JSON only, shaped by AgentResponse. See docs for details.
- ChromaDB writes to ./chroma_db by default and is ignored by git.