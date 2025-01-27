import os

from .base_llm import LLM


class DeepSeekLLM(LLM):
    def __init__(self, model_name='deepseek-chat', api_key=None, **kwargs):
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError('Please install openai with "pip install openai"')

        if not api_key:
            api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("API key is required")
        self.model_name = model_name
        self.client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        super().__init__(**kwargs)

    def _generate(self, messages, **kwargs):
        return self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            **kwargs
        ).choices[0].message.content
