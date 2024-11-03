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
        super().__init__(self.name, self.description, **kwargs)

    def run(self, query: str) -> list:
        '''
        :param query: The search query e.g. query="Python programming" or query="Coffee site:wikipedia.org"
        '''
        params: dict = {
            "engine": 'google',
            "google_domain": "google.com",
            "gl": "us",
            "hl": "en",
            "q": query,
            "api_key": self.api_key
        }

        search = GoogleSearch(params)
        response = search.get_dict()
        if 'organic_results' not in response:
            return []
        return [dict(title=r['title'], link=r['link'], snippet=r['snippet']) for r in response['organic_results']]
