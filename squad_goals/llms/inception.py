import os
import requests

from .base_llm import LLM


class InceptionLLM(LLM):
    def __init__(self, model_name='mercury-coder-small', api_key=None, **kwargs):
        if not api_key:
            api_key = os.getenv("INCEPTION_API_KEY")
        if not api_key:
            raise ValueError("API key is required")
            
        self.model_name = model_name
        self.api_key = api_key
        self.base_url = "https://api.inceptionlabs.ai/v1"
        super().__init__(**kwargs)

    def _generate(self, messages, **kwargs):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messages": messages,
            "model": self.model_name
        }
        
        # Add any additional parameters from kwargs
        payload.update({k: v for k, v in kwargs.items() if k not in ["messages", "model"]})
        
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload
        )
        
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"] 