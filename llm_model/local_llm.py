import urllib.request
import urllib.error
import json

class LocalLLM:
    def __init__(
        self,
        model: str = "llama3.2",
        base_url: str = "http://localhost:11434",
    ):
        """
        Initialize a local LLM client using Ollama.

        Ollama runs models locally on your machine with a simple REST API.
        No API key needed — everything runs on your hardware.

        Setup:
            1. Install Ollama: https://ollama.com
            2. Pull a model: `ollama pull llama3.2`
            3. Ollama starts automatically; verify with `ollama list`

        :param model: Name of the locally available Ollama model.
                      Run `ollama list` to see what you have pulled.
                      Popular choices: llama3.2, mistral, gemma2, phi3
        :param base_url: Ollama server URL (default: localhost:11434).
        """
        self.model = model
        self.base_url = base_url.rstrip("/")

    async def invoke_model(self, messages: list[dict]) -> str:
        """
        Invoke a local Ollama model with a list of messages.

        Ollama's /api/chat endpoint accepts the same message format as OpenAI —
        roles can be "system", "user", or "assistant" — so no conversion needed.

        :param messages: List of message dicts with "role" and "content" keys.
        :return: The model's text response as a string.
        """
        if not messages:
            raise ValueError("Messages list cannot be empty")

        url = f"{self.base_url}/api/chat"
        payload = json.dumps({
            "model": self.model,
            "messages": messages,
            "stream": False,
        }).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=120) as response:
                result = json.loads(response.read().decode())
        except urllib.error.URLError as e:
            raise RuntimeError(
                f"Could not connect to Ollama at {self.base_url}. "
                f"Is Ollama running? Try `ollama serve` in a terminal. Error: {e}"
            )

        return result["message"]["content"].strip()

    async def list_models(self) -> list[str]:
        """
        Returns a list of model names available in the local Ollama instance.
        Useful for checking what's pulled before initializing.
        """
        url = f"{self.base_url}/api/tags"
        req = urllib.request.Request(url, method="GET")
        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode())
            return [m["name"] for m in result.get("models", [])]
        except Exception as e:
            raise RuntimeError(f"Could not list Ollama models: {e}")