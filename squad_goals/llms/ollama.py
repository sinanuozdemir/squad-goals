from .base_llm import LLM

class OllamaLLM(LLM):
    def __init__(self, model_name="llama3.2", **kwargs):
        try:
            import ollama
        except ImportError:
            raise ImportError("Please install ollama with `pip install ollama`")
        self.client = ollama
        self.model_name = model_name
        super().__init__(**kwargs)

    def _generate(self, messages, **kwargs):
        response = self.client.chat(model=self.model_name, messages=messages, options=kwargs)
        return response['message']['content']
