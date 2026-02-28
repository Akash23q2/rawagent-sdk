# llm_model

Thin wrappers over various LLM providers. All clients implement the same interface:

```python
async invoke_model(messages: list[dict]) -> str
```

This makes them drop-in replacements for each other inside `BuildAgent`.

---

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
- `base_url` defaults to NVIDIA's Integrate endpoint; override if using OpenAI or a different gateway
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
- Works with any OpenAI-compatible API — swap `base_url` to point at OpenAI directly, a local proxy, or another gateway.

---

## Gemini
Location: `llm_model/Gemini.py`
Dependency: `pip install google-generativeai`

### Initialization
```python
Gemini(
  api_key: str,
  model: str = "gemini-1.5-flash",
)
```
- Get your API key from [Google AI Studio](https://aistudio.google.com)
- Other model options: `gemini-1.5-pro`, `gemini-2.0-flash`

### Method
- `async invoke_model(messages: list[dict]) -> str`
  - Accepts the same message format as OpenAI (`system`/`user`/`assistant` roles)
  - Internally converts to Gemini's format: `system` prompt is prepended to the first `user` message; `assistant` roles become `model`

### Usage
```python
from llm_model.Gemini import Gemini

client = Gemini(api_key="<your-key>")
response = await client.invoke_model([
  {"role": "system", "content": "You are helpful and answer in JSON."},
  {"role": "user", "content": "Say hello as {\"text\": \"hi\"}"},
])
print(response)
```

### Notes
- Gemini has no dedicated system role in its API — the system prompt gets merged into the first user turn automatically.
- Gemini uses `"model"` instead of `"assistant"` for AI turns internally; this conversion is handled for you.
- Multi-turn conversation history is passed via `start_chat(history=[...])`, with the latest message sent separately.

---

## HuggingFace
Location: `llm_model/HuggingFace.py`
Dependency: none (uses stdlib `urllib`)

### Initialization
```python
HuggingFace(
  api_key: str,
  model: str = "mistralai/Mistral-7B-Instruct-v0.3",
  base_url: str = "https://api-inference.huggingface.co/models",
  max_new_tokens: int = 1024,
)
```
- Get your token from [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
- Other model options: `meta-llama/Meta-Llama-3-8B-Instruct`, `google/gemma-2-9b-it`
- Free tier has rate limits; upgrade to HF PRO or use Inference Endpoints for production

### Method
- `async invoke_model(messages: list[dict]) -> str`
  - Accepts the standard message list format
  - Internally converts to a raw prompt string using `[INST]...[/INST]` chat template
  - Sets `return_full_text: False` so only the generated response is returned, not the prompt

### Usage
```python
from llm_model.HuggingFace import HuggingFace

client = HuggingFace(api_key="<your-hf-token>")
response = await client.invoke_model([
  {"role": "system", "content": "You are helpful and answer in JSON."},
  {"role": "user", "content": "Say hello as {\"text\": \"hi\"}"},
])
print(response)
```

### Notes
- HuggingFace's free inference API expects a raw prompt string, not a structured message list — the `[INST]` template conversion is done internally.
- Different model families use different chat templates. The `[INST]` format works for Mistral and Llama; if you use a very different model architecture, you may need to adjust `_build_prompt`.
- Not all models on the Hub are available on the free inference API. If you get a 503, the model may be loading — retry after a few seconds.

---

## LocalLLM
Location: `llm_model/LocalLLM.py`
Dependency: [Ollama](https://ollama.com) running locally

### Initialization
```python
LocalLLM(
  model: str = "llama3.2",
  base_url: str = "http://localhost:11434",
)
```
- No API key needed — runs entirely on your machine
- Setup: install Ollama, then `ollama pull <model>`
- Popular models: `llama3.2`, `mistral`, `gemma2`, `phi3`

### Methods
- `async invoke_model(messages: list[dict]) -> str`
  - Accepts the standard message list format
  - Ollama natively supports `system`/`user`/`assistant` roles — no conversion needed
  - Uses `stream: false` to return a single complete response
- `async list_models() -> list[str]`
  - Returns names of all models currently pulled in your local Ollama instance
  - Useful for verifying a model is available before initializing

### Usage
```python
from llm_model.LocalLLM import LocalLLM

client = LocalLLM(model="llama3.2")
response = await client.invoke_model([
  {"role": "system", "content": "You are helpful and answer in JSON."},
  {"role": "user", "content": "Say hello as {\"text\": \"hi\"}"},
])
print(response)
```

### Notes
- Ollama must be running before making calls (`ollama serve` if it didn't start automatically).
- The timeout is set to 120 seconds — local models can be slow on first load or on weaker hardware.
- If you get a connection error, run `ollama list` to confirm the service is up and the model is pulled.
- Ollama also exposes an OpenAI-compatible endpoint at `http://localhost:11434/v1` — you could use the `OpenAi` client pointing at that URL instead, but `LocalLLM` uses the native endpoint directly.