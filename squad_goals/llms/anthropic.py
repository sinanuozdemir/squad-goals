import os

from .base_llm import LLM


class AnthropicLLM(LLM):
    def __init__(self, model_name="claude-3-opus-20240229", api_key=None, **kwargs):
        try:
            from anthropic import Anthropic
        except ImportError:
            raise ImportError(
                "`anthropic` package not found, please run `pip install anthropic`"
            )
        if not api_key:
            api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("Anthropic API key is required")

        self.model_name = model_name
        self.client = Anthropic(api_key=api_key)
        super().__init__(**kwargs)

    def _generate(self, messages, **kwargs):
        """
        Sends a prompt to Claude and returns the generated response.
        :param messages: List of dictionaries, where each dictionary represents a message with 'role' and 'content'.
        :return: Generated text from Claude.
        """
        # Convert the input message format if necessary
        if 'stop' in kwargs:
            kwargs['stop_sequences'] = kwargs.pop('stop')

        anthropic_messages = []
        for message in messages:
            role = message['role']
            content = message['content']
            # Only 'user' and 'assistant' roles are required for Claude
            if role == 'system':
                anthropic_messages.append({"role": "user", "content": "You are a helpful assistant."})
            anthropic_messages.append({"role": role, "content": content})

        if 'max_tokens' not in kwargs:
            kwargs['max_tokens'] = 4096

        # Make a request to Claude via Anthropic's API
        response = self.client.messages.create(
            model=self.model_name,
            messages=anthropic_messages,
            **kwargs
        )

        # Return the response text
        return response.content[0].text
