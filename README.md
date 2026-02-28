# rawagent-sdk

<!-- PROJECT HERO IMAGE -->
![rawagent-sdk](/rawagent-sdk/src/rawagent.png)


### A lightweight, agentic AI framework for Python focused on tool-use, structured LLM responses, human-in-the-loop workflows, semantic memory (ChromaDB), and optional MCP tool integration.

### The idea was simple: most agent frameworks are too heavy or too opinionated. This one gives you just enough structure to build something real, while keeping every piece inspectable and replaceable.

---

## Features
- BuildAgent orchestrates conversations, tool calling, retries, and error handling
- Output (AgentResponse) to enforce JSON-only LLM outputs. No
- Tool registry (Tools) with automatic argument type strict schema generation and validator for correct function signatures.
- Human-in-the-loop utility for interactive clarification and decisions to avoid hallucinations.
- Semantic memory via ChromaDB (add, query, delete, list)
- MCP client wrapper for stdio-based external tool servers
- Pretty logging for tool/LLM/memory events
- Multiple LLM backends , OpenAI-compatible APIs, Gemini, HuggingFace, or local models via Ollama

---

## What it does

- **BuildAgent** runs the core loop: send query → get structured JSON response → call tools → feed results back -> repeat until done
- **AgentResponse** (Pydantic schema) forces the LLM to output structured JSON so tool calls are reliable and predictable
- **Tools registry** auto-generates argument schemas from Python function type hints -> just write a function, decorate it, done
- **Semantic memory** via ChromaDB -> the agent can store and recall facts across sessions
- **Human-in-the-loop** -> agent can pause and ask you for clarification mid-task
- **MCP support** -> plug in external tool servers via stdio (Model Context Protocol)

---

## In Action

[![Watch the demo](https://img.youtube.com/vi/_Ca9Yh0w92U/0.jpg)](https://youtu.be/_Ca9Yh0w92U)
---

## Setup

### Using uv (recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package manager — significantly faster than pip for resolving and installing dependencies.

Install uv if you don't have it:

```bash
# macOS / Linux
curl -Ls https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Then set up the project:

```bash
git clone https://github.com/your-username/rawagent-sdk
cd rawagent-sdk

uv venv                          # creates .venv in the project folder
source .venv/bin/activate        # Windows: .venv\Scripts\activate

uv pip install -e .              # installs project + all deps from pyproject.toml
```

### Using pip

```bash
pip install -U chromadb mcp openai pydantic python-dotenv google-generativeai
```

---

## Environment setup

Create a `.env` file in the project root:

```bash
touch .env
```

Add your keys — only fill in the ones you plan to use:

```env
# Required: your main LLM provider key
API_KEY=your_openai_or_nvidia_key_here

# Optional: only needed if using the Gemini client
GEMINI_API_KEY=your_google_ai_studio_key_here

# Optional: only needed if using the HuggingFace client
HF_API_KEY=your_huggingface_token_here
```

The project uses `python-dotenv` — calling `load_dotenv()` at the top of your script will load these automatically into `os.environ`.

> **Never commit your `.env` file.** Add `.env` to your `.gitignore`.

---

## Quickstart

```python
from agent_core import BuildAgent
from agent_tools import Tools
from llm_model.OpenAi import OpenAi

def search_docs(query: str, top_k: int = 3) -> list[str]:
    """Search internal docs for a query and return top_k snippets."""
    corpus = [
        "RawAgent SDK lets you build agentic workflows.",
        "Tools are registered from Python callables with type hints.",
        "ChromaDB powers semantic memory for the agent.",
    ]
    return [t for t in corpus if query.lower() in t.lower()][:top_k]

tools = Tools()
tools.add_tool(search_docs)

import os
llm = OpenAi(api_key=os.environ["API_KEY"])

agent = BuildAgent(
    name="RawAgent",
    description="General-purpose agent with tools and memory",
    llm_client=llm,
    tools=tools,
    enable_human_in_loop=True,
    memory_collection_name="demo_memory",
)

result = agent.run_agent_sync("Find references about tools and memory")
print(result)
```

---

## Example file

`example.py` is a ready-to-run demo showing how to wire up a real tool. It uses the pyttsx3 so make sure its downloaded before running:

```bash
pip install pyttsx3
```
```bash
python example.py
```

The agent can answer questions like *"what's the weather in Tokyo?"* or *"is it raining in London?"* using real-time data. It's a minimal but complete example of the full stack: LLM → tool call → API → response.

---

## LLM backends

All clients implement the same `async invoke_model(messages: list[dict]) -> str` interface, so they're drop-in replacements in `BuildAgent`.

| File | Backend | Notes |
| :--- | :--- | :--- |
| `llm_model/OpenAi.py` | OpenAI / NVIDIA / any OpenAI-compatible API | Default |
| `llm_model/Gemini.py` | Google Gemini | Requires `google-generativeai` |
| `llm_model/HuggingFace.py` | HuggingFace Inference API | Hosted models via REST |
| `llm_model/LocalLLM.py` | Local models via Ollama | No API key needed |

---

## Docs

- [agent_core — BuildAgent, memory, prompt utilities](docs/agent_core.md)
- [agent_tools — Tools registry, MCP integration](docs/agent_tools.md)
- [llm_model — LLM client wrappers](docs/llm_model.md)

---

## Notes

- The agent expects JSON-only output shaped by `AgentResponse`. See [agent_core docs](docs/agent_core.md) for the full schema.
- ChromaDB writes to `./chroma_db` by default — add it to `.gitignore`.

---

## Contributing

Contributions are welcome. Open an issue or submit a pull request.

## License

MIT License

---

If you like the project, give it a star ⭐