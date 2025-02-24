import os

import requests

from .base_tool import BaseTool



class ReversePhoneLookupTool(BaseTool):
    def __init__(self, **kwargs):
        self.name = "Reverse Phone Lookup Tool"
        self.description = "This tool takes in a phone number and returns information about the owner if available on this service"
        super().__init__(self.name, self.description, **kwargs)

    def run(self, phone: str) -> dict:
        '''
        :param phone: The phone number to lookup. Include country code e.g. phone="16094626706" or phone="14158675309"
        '''
        url = "https://caller-id-social-search-eyecon.p.rapidapi.com/"

        querystring = {"phone": phone}

        headers = {
            "x-rapidapi-key": os.getenv("RAPID_API_KEY"),
            "x-rapidapi-host": "caller-id-social-search-eyecon.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers, params=querystring)

        return response.json().get('response')
