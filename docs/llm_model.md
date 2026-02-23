# llm_model

Thin wrapper over the `openai` client to invoke chat-completions compatible models.

## OpenAi
Location: `llm_model/OpenAi.py`

### Initialization
```python
OpenAi(
  api_key: str,
  base_url: str = "https://integrate.api.nvidia.com/v1",
  model: str = "openai/gpt-oss-20b",
)
```
- `base_url` defaults to NVIDIA’s Integrate endpoint; override if using OpenAI or a different gateway
- Stores the client and model name; validates that the client is initialized before use

### Method
- `async invoke_model(messages: list[dict]) -> str`
  - Accepts a standard Chat Completions message list: `[{"role": "system"|"user"|"assistant", "content": "..."}, ...]`
  - Streams tokens and aggregates them into a full string response
  - The agent expects this to be valid JSON (per the system prompt) when used with `BuildAgent`

### Usage
```python
from llm_model.OpenAi import OpenAi

client = OpenAi(api_key="<your-key>")
response = await client.invoke_model([
  {"role": "system", "content": "You are helpful and answer in JSON."},
  {"role": "user", "content": "Say hello as {\"text\": \"hi\"}"},
])
print(response)
```

### Notes
- Although defined `async`, the underlying client call is synchronous; the method aggregates streamed chunks internally.
- Pair this client with `agent_core.BuildAgent` to enforce JSON-only outputs via the embedded `AgentResponse` schema in the system prompt.
