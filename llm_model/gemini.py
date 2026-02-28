import google.generativeai as genai

class Gemini:
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        """
        Initialize the Gemini client.
        
        :param api_key: Your Google AI Studio API key.
        :param model: Gemini model name (default: gemini-1.5-flash).
                      Other options: gemini-1.5-pro, gemini-2.0-flash
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
        self.model_name = model

    async def invoke_model(self, messages: list[dict]) -> str:
        """
        Invoke the Gemini model with a list of messages.

        The messages follow the standard OpenAI format:
            [{"role": "system"|"user"|"assistant", "content": "..."}]

        Gemini uses a different role naming ("user"/"model") and doesn't support
        a dedicated system role — so we prepend the system prompt to the first
        user message instead.

        :param messages: List of message dicts with "role" and "content" keys.
        :return: The model's text response as a string.
        """
        if not messages:
            raise ValueError("Messages list cannot be empty")

        # Extract system prompt if present
        system_content = ""
        chat_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_content = msg["content"]
            else:
                chat_messages.append(msg)

        # Convert to Gemini's format: roles must be "user" or "model"
        gemini_history = []
        for msg in chat_messages[:-1]:  # all but the last message go into history
            role = "model" if msg["role"] == "assistant" else "user"
            gemini_history.append({"role": role, "parts": [msg["content"]]})

        # The last message is the current prompt
        last_message = chat_messages[-1]["content"] if chat_messages else ""

        # Prepend system prompt to the first user turn if present
        if system_content and gemini_history and gemini_history[0]["role"] == "user":
            gemini_history[0]["parts"][0] = system_content + "\n\n" + gemini_history[0]["parts"][0]
        elif system_content and not gemini_history:
            last_message = system_content + "\n\n" + last_message

        chat = self.model.start_chat(history=gemini_history)
        response = chat.send_message(last_message)
        return response.text