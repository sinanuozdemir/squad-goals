import json
import os


class LLM:

    def __init__(self, warehouse=None):
        self.warehouse = warehouse

    def _generate(self, messages, **kwargs):
        raise NotImplementedError("generate method must be implemented in subclass")

    def generate(self, messages, **kwargs):
        raw_text_response = self._generate(messages, **kwargs)
        if self.warehouse:
            if self.warehouse == 'supabase':
                # check for supabase environment variables
                if 'SUPABASE_URL' not in os.environ or 'SUPABASE_KEY' not in os.environ:
                    raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables must be set")
                try:
                    from supabase import create_client, Client
                except ImportError:
                    raise ImportError("Please install supabase with `pip install supabase-py`")
                supabase_table = os.environ.get('SUPABASE_TABLE', 'cost_projecting')
                # find all class variables and add to a dictionary
                class_vars = {}
                for key, value in self.__dict__.items():
                    if type(value) in (str, int, float, bool, list, dict) and not key.startswith('_'):
                        class_vars[key] = value

                class_vars.update(kwargs)
                supabase_url = os.environ['SUPABASE_URL']
                supabase_key = os.environ['SUPABASE_KEY']
                supabase_client: Client = create_client(supabase_url, supabase_key)
                supabase_client.table(supabase_table).insert({
                    'prompt': json.dumps(messages),
                    'response': raw_text_response,
                    'inference_params': class_vars,
                    'model': self.__class__.__name__
                }).execute()
        return raw_text_response
