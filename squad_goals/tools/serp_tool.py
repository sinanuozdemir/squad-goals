# SerpAPI tool
try:
    from serpapi import GoogleSearch
except ImportError:
    raise ImportError('Please install serpapi with "pip install google-search-results"')
import os

from .base_tool import BaseTool


class SerpTool(BaseTool):
    def __init__(self, api_key=None, **kwargs):
        if not api_key:
            api_key = os.getenv("SERP_API_KEY")
        if not api_key:
            raise ValueError("API key is required")
        self.api_key = api_key
        self.name = "SerpAPI Tool"
        self.description = "This tool uses SerpAPI to get search results from Google"
        self.engine = 'google'
        super().__init__(self.name, self.description, **kwargs)

    def _search(self, query: str, **kwargs) -> dict:

        params: dict = {
            "engine": self.engine,
            "google_domain": "google.com",
            "gl": "us",
            "hl": "en",
            "q": query,
            "api_key": self.api_key
        }
        params.update(kwargs)

        search = GoogleSearch(params)
        return search.get_dict()

    def run(self, query: str) -> list:
        '''
        :param query: The search query e.g. query="Python programming" or query="Coffee site:wikipedia.org"
        '''
        response = self._search(query)
        if 'organic_results' not in response:
            return []
        return [dict(title=r['title'], link=r['link'], snippet=r['snippet']) for r in response['organic_results']]



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

