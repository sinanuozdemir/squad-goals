import re
from copy import copy

import requests

from .base_tool import BaseTool


class APITool(BaseTool):
    def __init__(
            self,
            api_url: str,
            api_key: str,
            api_header_key: str = 'Authorization',
            api_header_value: str = 'Bearer',
            name: str = "API Tool",
            api_method='POST',
            description: str = "This tool uses an API to get information",
            **kwargs
    ):
        self.api_url = api_url
        self.api_key = api_key
        self.api_header_key = api_header_key
        self.api_header_value = api_header_value
        self.api_method = api_method.upper()
        # using regex, check for {business_id} or other variables in the url and save
        re_pattern = r'{(\w+)}'
        self.url_variables = re.findall(re_pattern, api_url)

        super().__init__(name, description, **kwargs)

    def run(self, api_payload: dict = None, **kwargs) -> dict:
        headers = {
            self.api_header_key: f"{self.api_header_value} {self.api_key}"
        } if self.api_key else {}
        # replace url variables with values from kwargs, raise error if not found
        if len(set(self.url_variables) - set(kwargs.keys())) > 0:
            raise ValueError(f"URL variables {set(self.url_variables) - set(kwargs.keys())} not found in kwargs")
        url_to_use = copy(self.api_url)
        for url_var in self.url_variables:
            url_to_use = url_to_use.replace(f"{{{url_var}}}", kwargs[url_var])
        response = getattr(requests, self.api_method.lower())(url_to_use, headers=headers, json=api_payload)
        return response.json()

    # base tool has _describe_run, but add the url variables here so they know to set it
    def _describe_run(self):
        base_description = super()._describe_run()
        return f"{base_description}\nURL Variables that must be passed as well: {', '.join(self.url_variables)}"
