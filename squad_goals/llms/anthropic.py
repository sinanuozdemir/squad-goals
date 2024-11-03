import os

from anthropic import Anthropic

from .base_llm import LLM


class AnthropicLLM(LLM):
    def __init__(self, model_name="claude-3-opus-20240229", api_key=None):
        if not api_key:
            api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("Anthropic API key is required")

        self.model_name = model_name
        self.client = Anthropic(api_key=api_key)

    def generate(self, messages, max_tokens=1024, **kwargs):
        """
        Sends a prompt to Claude and returns the generated response.
        :param messages: List of dictionaries, where each dictionary represents a message with 'role' and 'content'.
        :param max_tokens: Maximum number of tokens to generate in response.
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

        # Make a request to Claude via Anthropic's API
        response = self.client.messages.create(
            model=self.model_name,
            max_tokens=max_tokens,
            messages=anthropic_messages,
            **kwargs
        )

        # Return the response text
        return response.content[0].text
