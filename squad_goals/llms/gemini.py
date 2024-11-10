import os

from .base_llm import LLM


class GeminiLLM(LLM):
    def __init__(self, model_name="gemini-1.5-flash", api_key=None):
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError(
                "`google-generativeai` package not found, please run `pip install google-generativeai`"
            )
        if not api_key:
            api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Gemini API key is required.")
        genai.configure(api_key=api_key)
        self.model_name = model_name
        self.client = genai.GenerativeModel(model_name)

    def generate(self, messages, max_output_tokens=1024, stop=None, **kwargs):
        """
        Sends a prompt to the Gemini model and returns the generated response.
        :param messages: List of dictionaries, each with 'role' and 'content'.
        :param max_output_tokens: Maximum number of tokens to generate in response.
        :param stop_sequences: List of strings where the model will stop generating further tokens.
        :param kwargs: Additional arguments to pass to the API.
        :return: Generated text from the Gemini model.
        """
        import google.generativeai as genai
        if messages[-1]['role'] != 'user':
            raise ValueError("The last message in the conversation history must be from the user.")

        # Convert messages to the format expected by the SDK
        history = [{"role": 'model' if msg['role'] == 'assistant' else msg['role'], "parts": [msg['content']]} for msg
                   in messages[:-1]]

        # Start a chat session with the existing history
        chat = self.client.start_chat(history=history)

        # Prepare the generation configuration
        generation_config = genai.types.GenerationConfig(
            max_output_tokens=max_output_tokens,
            stop_sequences=stop,
            **kwargs
        )

        # Send the final user message and get the response
        response = chat.send_message(
            messages[-1]["content"],  # Pass the content directly
            generation_config=generation_config
        )
        return response.candidates[0].content.parts[0].text
