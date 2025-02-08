import os

import requests

from .serp_tool import SerpTool, BaseTool


# a sub-tool of SerpTool where engine is set to google_reverse_image and we need the 'image_url' parameter
class ReverseImageSearchTool(SerpTool):
    def __init__(self, api_key=None, **kwargs):
        super().__init__(api_key, **kwargs)
        self.engine = 'google_reverse_image'
        self.name = "Reverse Image Search Tool"
        self.description = "This tool should be used to reverse search an image to find where it is used on the web."

    def run(self, image_url: str) -> list:
        '''
        :param image_url: The URL of the image to search for
        '''
        response = self._search(query=None, image_url=image_url)
        if 'image_results' not in response:
            return []
        return [dict(title=r['title'], link=r['link'], snippet=r['snippet']) for r in response['image_results']]


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
