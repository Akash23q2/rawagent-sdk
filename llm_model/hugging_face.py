import urllib.request
import urllib.error
import json

class HuggingFace:
    def __init__(
        self,
        api_key: str,
        model: str = "mistralai/Mistral-7B-Instruct-v0.3",
        base_url: str = "https://api-inference.huggingface.co/models",
        max_new_tokens: int = 1024,
    ):
        """
        Initialize the HuggingFace Inference API client.
        """
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.max_new_tokens = max_new_tokens

    async def invoke_model(self, messages: list[dict]) -> str:
        """
        Invoke a HuggingFace hosted model with a list of messages.
        """
        if not messages:
            raise ValueError("Messages list cannot be empty")

        prompt = self._build_prompt(messages)

        url = f"{self.base_url}/{self.model}"
        payload = json.dumps({
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": self.max_new_tokens,
                "return_full_text": False,
                "do_sample": True,
                "temperature": 0.7,
            }
        }).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=payload,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode())
        except urllib.error.HTTPError as e:
            error_body = e.read().decode()
            raise RuntimeError(f"HuggingFace API error {e.code}: {error_body}")

        if isinstance(result, list) and result:
            return result[0].get("generated_text", "").strip()
        raise RuntimeError(f"Unexpected response format: {result}")

    def _build_prompt(self, messages: list[dict]) -> str:
        """
        Convert a message list into a prompt string using [INST] chat format.
        Compatible with Mistral, Llama 2/3, and many other instruct models.
        """
        prompt = ""
        system_content = ""

        for msg in messages:
            role = msg["role"]
            content = msg["content"]

            if role == "system":
                system_content = content
            elif role == "user":
                if system_content:
                    content = f"{system_content}\n\n{content}"
                    system_content = ""
                prompt += f"[INST] {content} [/INST]"
            elif role == "assistant":
                prompt += f" {content} "

        return prompt.strip()