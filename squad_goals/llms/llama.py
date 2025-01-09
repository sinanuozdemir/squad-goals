import requests

from .base_llm import LLM


class CustomLlama(LLM):
    def __init__(self, url, **kwargs):
        self.url = url
        super().__init__(**kwargs)

    def _generate(self, messages, stop, **kwargs):
        headers = {"Content-Type": "application/json"}
        messages = {
            'system': messages[0]['content'] if messages[0]['role'] == 'system' else 'You are a helpful assistant',
            'user': messages[1]['content'] if len(messages) > 1 and messages[1]['role'] == 'user' else messages[0][
                'content'],
            'stop_pattern': stop
        }
        response = requests.post(self.url, headers=headers, json=messages)
        response.raise_for_status()
        return response.text
